import 'dart:math' as math;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'main.dart';

// PG Robotics Bomber: fictional top-down arcade. Game numbers do not represent
// aircraft, weapons, navigation, or physical-world performance.
class MissionGameView extends StatefulWidget {
  const MissionGameView({super.key, required this.ukrainian,
    required this.active, this.initialModel = 0});
  final bool ukrainian;
  final bool active;
  final int initialModel;
  @override
  State<MissionGameView> createState() => _MissionGameViewState();
}

class _GroundTarget {
  _GroundTarget(this.x, this.y, this.kind, this.hp, this.velocity,
      this.shotClock, this.phase);
  double x, y, hp, velocity, shotClock, phase;
  final int kind; // 0 jeep, 1 truck, 2 armored vehicle, 3 turret
  double life = 0;
  double get radius => kind == 2 ? .038 : kind == 1 ? .035 : .028;
  double get maxHp => kind == 3 ? 3.4 : kind == 2 ? 5.1 : kind == 1 ? 2.7 : 1.7;
}
class _GroundShot {
  _GroundShot(this.x, this.y, this.vx, this.vy);
  double x, y, vx, vy;
}
class _FallingCharge {
  _FallingCharge(this.x, this.y, this.radius, this.power);
  final double x, y, radius, power;
  double progress = 0;
}
class _Ring {
  _Ring(this.x, this.y, this.radius, this.color, this.life);
  final double x, y, radius;
  final Color color;
  double life;
}
class _AirPickup {
  _AirPickup(this.x, this.y, this.kind);
  double x, y;
  final int kind; // repair, shield, boost, model
}

class _MissionGameViewState extends State<MissionGameView>
    with SingleTickerProviderStateMixin, WidgetsBindingObserver {
  static const String _bestKey = 'pg_bomber_highscore_v1';
  final math.Random _random = math.Random();
  final ValueNotifier<int> _frame = ValueNotifier<int>(0);
  final List<_GroundTarget> _targets = [];
  final List<_GroundShot> _shots = [];
  final List<_FallingCharge> _charges = [];
  final List<_AirPickup> _pickups = [];
  final List<_Ring> _rings = [];
  late final AnimationController _ticker;
  DateTime? _previous;
  bool _playing = false;
  bool _finished = false;
  bool _began = false;
  int _model = 0, _score = 0, _best = 0, _kills = 0;
  double _playerX = .5, _playerY = .69;
  double _hp = 100, _shield = 0, _boost = 0, _time = 0,
      _spawnClock = 0, _pickupClock = 0, _bombClock = 0, _hudClock = 0,
      _invuln = 0;
  int _boostStacks = 0, _shieldStacks = 0;
  String _flash = '';
  double _flashUntil = 0;
  int get _wave => 1 + (_time / 23).floor();
  String get _modelName => _model == 0 ? 'Lucky Strike 1.5' : 'Lucky Strike 2';
  double get _blastRadius => _model == 0
      ? (_boost > 0 ? .090 : .073)
      : (_boost > 0 ? .154 : .132);
  double get _blastPower => _model == 0
      ? (_boost > 0 ? 1.85 : 1.48)
      : (_boost > 0 ? 3.75 : 3.08);
  double get _releaseInterval => _model == 0
      ? (_boost > 0 ? .82 : 1.10)
      : (_boost > 0 ? .66 : .93);
  double get _targetRange => _model == 0 ? .215 : .258;

  @override
  void initState() {
    super.initState();
    _model = widget.initialModel.clamp(0, 1).toInt();
    WidgetsBinding.instance.addObserver(this);
    _ticker = AnimationController(vsync: this,
        duration: const Duration(minutes: 30))..addListener(_tick);
    _loadScore();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted && widget.active) _start(reset: true);
    });
  }
  Future<void> _loadScore() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) setState(() => _best = prefs.getInt(_bestKey) ?? 0);
  }
  Future<void> _saveScore() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_bestKey, _best);
  }
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state != AppLifecycleState.resumed) _pause();
  }
  @override
  void didUpdateWidget(covariant MissionGameView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.active && !widget.active) _pause();
  }
  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _ticker.dispose();
    _frame.dispose();
    super.dispose();
  }
  void _showFlash(String message, [double seconds = 1.7]) {
    _flash = message;
    _flashUntil = _time + seconds;
  }
  void _start({bool reset = false}) {
    if (reset || !_began || _finished) {
      _targets.clear(); _shots.clear(); _charges.clear();
      _pickups.clear(); _rings.clear();
      _model = widget.initialModel.clamp(0, 1).toInt();
      _time = 0; _score = 0; _kills = 0; _hp = 100;
      _shield = 0; _boost = 0; _boostStacks = 0; _shieldStacks = 0;
      _spawnClock = 0; _pickupClock = 0; _bombClock = 0;
      _invuln = 0; _playerX = .5; _playerY = .69;
      _hudClock = 0;
      _showFlash(widget.ukrainian ? 'АВТОСКИДАННЯ АКТИВНЕ' : 'AUTO RELEASE ACTIVE', 2.5);
    }
    _previous = DateTime.now();
    HapticFeedback.selectionClick();
    setState(() { _playing = true; _finished = false; _began = true; });
    _ticker.repeat();
  }
  void _pause() {
    if (!_playing) return;
    _ticker.stop();
    if (_score > _best) _best = _score;
    _saveScore();
    if (mounted) setState(() => _playing = false);
  }
  void _end() {
    _ticker.stop(); _playing = false; _finished = true;
    if (_score > _best) _best = _score;
    _saveScore();
    HapticFeedback.heavyImpact();
    if (mounted) setState(() {});
  }
  // Entire playfield is one gesture surface. The drone follows one finger.
  // A nearby ground target triggers an automatic fictional arcade drop.
  void _move(Offset local, Size size) {
    if (!_playing || size.width <= 0 || size.height <= 0) return;
    _playerX = (local.dx / size.width).clamp(.065, .935).toDouble();
    _playerY = (local.dy / size.height).clamp(.095, .915).toDouble();
    _frame.value++;
  }
  void _spawnTarget() {
    if (_targets.length >= 17) return;
    final roll = _random.nextDouble();
    final kind = _wave > 3 && roll < .19 ? 3
        : _wave > 2 && roll < .43 ? 2 : roll < .69 ? 1 : 0;
    final hp = kind == 3 ? 3.4 : kind == 2 ? 5.1 : kind == 1 ? 2.7 : 1.7;
    final lane = _random.nextInt(4);
    final x = [.16, .385, .615, .84][lane] + (_random.nextDouble() - .5) * .045;
    _targets.add(_GroundTarget(x, -.09, kind, hp,
        kind == 3 ? .014 : kind == 2 ? .035 : kind == 1 ? .050 : .070,
        1.35 + _random.nextDouble() * 2.0, _random.nextDouble() * math.pi));
  }
  void _spawnPickup() {
    if (_pickups.length > 5) return;
    final roll = _random.nextDouble();
    final kind = _model == 0 && roll > .91 ? 3 : roll < .34 ? 0 : roll < .64 ? 1 : 2;
    _pickups.add(_AirPickup(.12 + _random.nextDouble() * .76, -.07, kind));
  }
  double _dist(double ax, double ay, double bx, double by) {
    // Horizontal and vertical coordinates use a slightly corrected visual metric.
    final dx = (ax - bx) * .9, dy = ay - by;
    return math.sqrt(dx * dx + dy * dy);
  }
  _GroundTarget? _nearestTarget() {
    _GroundTarget? chosen;
    double best = _targetRange;
    for (final e in _targets) {
      final d = _dist(_playerX, _playerY, e.x, e.y);
      if (d < best) { best = d; chosen = e; }
    }
    return chosen;
  }
  void _release(_GroundTarget target) {
    // Visible impact point, with arcade travel time and a moving ground target.
    final y = (target.y + target.velocity * .53).clamp(.035, .97).toDouble();
    _charges.add(_FallingCharge(target.x, y, _blastRadius, _blastPower));
    _rings.add(_Ring(target.x, y, _blastRadius,
        const Color(0x88FFDE19), .43));
    if (_charges.length > 12) _charges.removeAt(0);
  }
  void _impact(_FallingCharge charge) {
    _rings.add(_Ring(charge.x, charge.y, charge.radius,
        const Color(0xFFFFC454), .64));
    _rings.add(_Ring(charge.x, charge.y, charge.radius * .55,
        const Color(0xFFFFF2C6), .34));
    for (final target in List<_GroundTarget>.of(_targets)) {
      final distance = _dist(charge.x, charge.y, target.x, target.y);
      if (distance > charge.radius + target.radius * .55) continue;
      // A center hit does full game damage. Outer ring does half damage.
      final damage = distance <= charge.radius * .46
          ? charge.power : charge.power * .5;
      target.hp -= damage;
      if (target.hp <= 0) {
        _targets.remove(target);
        _kills++;
        _score += switch (target.kind) { 3 => 80, 2 => 65, 1 => 35, _ => 20 };
        _rings.add(_Ring(target.x, target.y, .048,
            const Color(0xFFFF8B62), .35));
      }
    }
    if (_score > _best) _best = _score;
    HapticFeedback.lightImpact();
  }
  void _takeDamage(double damage) {
    if (_invuln > 0 || _shield > 0) {
      _rings.add(_Ring(_playerX, _playerY, .052,
          const Color(0xFF65EDD5), .34));
      return;
    }
    _hp = math.max(0, _hp - damage);
    _invuln = .63;
    _rings.add(_Ring(_playerX, _playerY, .06,
        const Color(0xFFFF6572), .55));
    HapticFeedback.mediumImpact();
    if (_hp <= 0) _end();
  }
  void _collect(_AirPickup pickup) {
    _pickups.remove(pickup);
    if (pickup.kind == 0) {
      _hp = math.min(100.0, _hp + 28);
      _showFlash(widget.ukrainian ? 'РЕМОНТ +28 HP' : 'REPAIR +28 HP');
    } else if (pickup.kind == 1) {
      _shield = math.min(60.0, _shield + 7);
      _shieldStacks++;
      _showFlash(widget.ukrainian ? 'ЩИТ +7 с' : 'SHIELD +7 s');
    } else if (pickup.kind == 2) {
      _boost = math.min(60.0, _boost + 9);
      _boostStacks++;
      _showFlash(widget.ukrainian ? 'ПОСИЛЕННЯ +9 с' : 'BOOST +9 s');
    } else if (_model == 0) {
      _model = 1;
      _showFlash('LUCKY STRIKE 2', 2.6);
    }
    _score += 10;
    _rings.add(_Ring(pickup.x, pickup.y, .07,
        const Color(0xFF6BFFE4), .55));
    HapticFeedback.selectionClick();
  }
  void _tick() {
    if (!mounted || !_playing || !widget.active) return;
    final now = DateTime.now();
    final dt = _previous == null ? .016 :
        (now.difference(_previous!).inMicroseconds / 1000000).clamp(0.0, .040).toDouble();
    _previous = now;
    if (dt <= 0) return;
    _time += dt;
    _spawnClock += dt; _pickupClock += dt; _bombClock += dt;
    _hudClock += dt;
    _shield = math.max(0, _shield - dt);
    _boost = math.max(0, _boost - dt);
    _invuln = math.max(0, _invuln - dt);
    if (_shield == 0) _shieldStacks = 0;
    if (_boost == 0) _boostStacks = 0;
    if (_spawnClock > math.max(.59, 1.35 - _wave * .065)) {
      _spawnClock = 0;
      _spawnTarget();
    }
    if (_pickupClock > 10.6) {
      _pickupClock = 0; _spawnPickup();
    }
    for (final target in List<_GroundTarget>.of(_targets)) {
      target.life += dt;
      if (target.kind != 3) target.y += target.velocity * dt;
      else target.y += .012 * dt;
      target.x += math.sin(target.life * 1.7 + target.phase) * dt * .008;
      if (target.y > 1.10) { _targets.remove(target); continue; }
      target.shotClock -= dt;
      if (target.y > .05 && target.shotClock <= 0 && _shots.length < 35) {
        target.shotClock = math.max(.88, 2.7 - _wave * .11) + _random.nextDouble() * .7;
        final diffX = (_playerX - target.x) * .9;
        final diffY = _playerY - target.y;
        final length = math.max(.001, math.sqrt(diffX*diffX + diffY*diffY));
        final projectileSpeed = .22 + math.min(.075, _wave * .006);
        _shots.add(_GroundShot(target.x, target.y,
            diffX / length * projectileSpeed / .9,
            diffY / length * projectileSpeed));
      }
    }
    if (_bombClock >= _releaseInterval && _charges.length < 4) {
      final target = _nearestTarget();
      if (target != null) { _release(target); _bombClock = 0; }
    }
    for (final charge in List<_FallingCharge>.of(_charges)) {
      charge.progress += dt / .53;
      if (charge.progress >= 1) {
        _charges.remove(charge);
        _impact(charge);
      }
    }
    for (final shot in List<_GroundShot>.of(_shots)) {
      shot.x += shot.vx * dt; shot.y += shot.vy * dt;
      if (shot.x < -.1 || shot.x > 1.1 || shot.y < -.1 || shot.y > 1.1) {
        _shots.remove(shot); continue;
      }
      if (_dist(shot.x, shot.y, _playerX, _playerY) < .037) {
        _shots.remove(shot);
        _takeDamage(14);
        if (!_playing) return;
      }
    }
    for (final pickup in List<_AirPickup>.of(_pickups)) {
      pickup.y += dt * .115;
      if (_dist(pickup.x, pickup.y, _playerX, _playerY) < .064) {
        _collect(pickup);
      } else if (pickup.y > 1.08) {
        _pickups.remove(pickup);
      }
    }
    for (final ring in _rings) ring.life -= dt;
    _rings.removeWhere((ring) => ring.life <= 0);
    _frame.value++;
    if (_hudClock >= .12) {
      _hudClock = 0;
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    final ua = widget.ukrainian;
    return Material(color: Palette.background, child: SafeArea(
      bottom: true, top: true,
      child: Column(children: [
        Container(
          padding: const EdgeInsets.fromLTRB(10, 6, 10, 7),
          decoration: const BoxDecoration(color: Palette.background,
              border: Border(bottom: BorderSide(color: Palette.border))),
          child: Column(children: [
            Row(children: [
              IconButton(
                tooltip: ua ? 'Закрити' : 'Close',
                onPressed: () { _pause(); Navigator.of(context).pop(); },
                icon: const Icon(CupertinoIcons.xmark_circle_fill, size: 25)),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(_modelName, style: const TextStyle(
                    fontWeight: FontWeight.w900, fontSize: 14)),
                Text(ua ? 'БОМБЕР · АВТОСКИДАННЯ' : 'BOMBER · AUTO DROP',
                  style: const TextStyle(fontSize: 9.5,
                    fontWeight: FontWeight.w700, color: Palette.primary)),
              ])),
              Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                Text('HP ${_hp.ceil()} / 100', style: const TextStyle(
                    fontSize: 12, fontWeight: FontWeight.w900)),
                SizedBox(width: 108, height: 5,
                    child: ClipRRect(borderRadius: BorderRadius.circular(5),
                      child: LinearProgressIndicator(value: _hp / 100,
                        backgroundColor: Palette.border,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          _hp > 35 ? const Color(0xFF78E6B4) :
                          const Color(0xFFFF596A))))),
              ]),
              IconButton(
                onPressed: _playing ? _pause : (_finished ? null : () => _start()),
                icon: Icon(_playing ? CupertinoIcons.pause_fill :
                  CupertinoIcons.play_fill, color: Palette.primary)),
            ]),
            Row(children: [
              Expanded(child: Text('${ua ? 'ХВИЛЯ' : 'WAVE'} $_wave · ${ua ? 'ЦІЛІ' : 'TARGETS'} $_kills',
                style: const TextStyle(fontSize: 10, color: Palette.secondary))),
              Text('$_score  /  $_best',
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w900)),
              if (_shield > 0) Padding(padding: const EdgeInsets.only(left: 9),
                  child: Text('⬡${_shield.ceil()}с', style: const TextStyle(
                      color: Color(0xFF69F0D3), fontSize: 10))),
              if (_boost > 0) Padding(padding: const EdgeInsets.only(left: 8),
                  child: Text('✦${_boost.ceil()}с', style: const TextStyle(
                      color: Palette.primary, fontSize: 10))),
            ]),
          ]),
        ),
        Expanded(child: LayoutBuilder(builder: (context, box) {
          final size = Size(box.maxWidth, box.maxHeight);
          return GestureDetector(
            behavior: HitTestBehavior.opaque,
            onPanDown: (details) => _move(details.localPosition, size),
            onPanUpdate: (details) => _move(details.localPosition, size),
            onTapDown: (details) => _move(details.localPosition, size),
            child: Stack(fit: StackFit.expand, children: [
              AnimatedBuilder(animation: _frame, builder: (_, __) =>
                CustomPaint(painter: _BomberPainter(
                    targets: _targets, shots: _shots, charges: _charges,
                    pickups: _pickups, rings: _rings,
                    player: Offset(_playerX, _playerY), model: _model,
                    time: _time, shield: _shield > 0,
                    invulnerable: _invuln > 0,
                    range: _targetRange, blast: _blastRadius,
                    target: _nearestTarget(),
                )),
              ),
              if (_playing && _time < _flashUntil) Positioned(
                top: 15, left: 16, right: 16,
                child: IgnorePointer(child: Center(child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
                  decoration: BoxDecoration(color: const Color(0xE611191D),
                    border: Border.all(color: Palette.primary),
                    borderRadius: BorderRadius.circular(12)),
                  child: Text(_flash, textAlign: TextAlign.center,
                    style: const TextStyle(color: Palette.primary,
                        fontSize: 11, fontWeight: FontWeight.w900))))),
              ),
              if (!_playing) ColoredBox(color: const Color(0xD9081015),
                child: Center(child: Padding(
                  padding: const EdgeInsets.all(26),
                  child: Column(mainAxisSize: MainAxisSize.min, children: [
                    Icon(_finished ? CupertinoIcons.refresh_circled :
                        CupertinoIcons.pause_circle, color: Palette.primary, size: 58),
                    const SizedBox(height: 13),
                    Text(_finished ? (ua ? 'МІСІЮ ЗАВЕРШЕНО' : 'MISSION OVER') :
                        (ua ? 'ПАУЗА' : 'PAUSED'),
                      style: const TextStyle(fontSize: 24,
                          fontWeight: FontWeight.w900), textAlign: TextAlign.center),
                    const SizedBox(height: 11),
                    Text(_finished ? '${ua ? 'Результат' : 'Score'}: $_score' :
                        (ua ? 'Один палець — рух дрона. Скидання автоматичне.' :
                            'One finger moves the drone. Drops are automatic.'),
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Palette.secondary,
                          fontSize: 12, height: 1.5)),
                    const SizedBox(height: 22),
                    YellowAction(title: _finished ? (ua ? 'Заново' : 'Restart') :
                        (ua ? 'Продовжити' : 'Continue'),
                      icon: CupertinoIcons.play_fill,
                      onTap: () => _start(reset: _finished)),
                  ]),
                )),
              ),
            ]),
          );
        })),
        Padding(padding: const EdgeInsets.fromLTRB(16, 8, 16, 9),
          child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            const Icon(CupertinoIcons.hand_draw, color: Palette.primary, size: 16),
            const SizedBox(width: 8),
            Flexible(child: Text(ua ?
                'Рух одним пальцем · скидання автоматичне · уникай пострілів' :
                'One finger · automatic drop · dodge incoming shots',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Palette.secondary, fontSize: 10))),
          ])),
      ]),
    ));
  }
}

class _BomberPainter extends CustomPainter {
  const _BomberPainter({required this.targets, required this.shots,
    required this.charges, required this.pickups, required this.rings,
    required this.player, required this.model, required this.time,
    required this.shield, required this.invulnerable,
    required this.range, required this.blast, required this.target});
  final List<_GroundTarget> targets;
  final List<_GroundShot> shots;
  final List<_FallingCharge> charges;
  final List<_AirPickup> pickups;
  final List<_Ring> rings;
  final Offset player;
  final int model;
  final double time, range, blast;
  final bool shield, invulnerable;
  final _GroundTarget? target;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    canvas.drawRect(rect, Paint()..shader = const LinearGradient(
      begin: Alignment.topLeft, end: Alignment.bottomRight,
      colors: [Color(0xFF253238), Color(0xFF142127), Color(0xFF10191D)],
    ).createShader(rect));
    final unit = math.min(size.width, size.height);
    Offset pt(double x, double y) => Offset(x * size.width, y * size.height);
    final ground = Paint()..color = const Color(0xFF405348).withValues(alpha: .25)
      ..style = PaintingStyle.stroke..strokeWidth = 1.0;
    for (var i = 0; i < 8; i++) {
      final x = (i + .5) * size.width / 8;
      final waviness = math.sin(i * 5 + time * .04) * 8;
      canvas.drawLine(Offset(x + waviness, 0),
          Offset(x - waviness, size.height), ground);
    }
    final roadPaint = Paint()..color = const Color(0xFF354345)..strokeWidth = 22;
    final middle = Paint()..color = const Color(0x527A8A75)..strokeWidth = 1.2;
    for (final lane in [.16, .385, .615, .84]) {
      final x = lane * size.width;
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), roadPaint);
      for (double y = (time * 36) % 46 - 46; y < size.height; y += 46) {
        canvas.drawLine(Offset(x, y), Offset(x, y + 18), middle);
      }
    }
    for (final enemy in targets) {
      _groundVehicle(canvas, pt(enemy.x, enemy.y), enemy);
    }
    for (final charge in charges) {
      final center = pt(charge.x, charge.y);
      final radius = charge.radius * unit;
      canvas.drawCircle(center, radius, Paint()
        ..color = const Color(0x40FFDE19)
        ..style = PaintingStyle.stroke..strokeWidth = 1.4);
      canvas.drawCircle(center, radius * .46, Paint()
        ..color = const Color(0x78FF7D59)
        ..style = PaintingStyle.stroke..strokeWidth = 1.0);
      final p = Offset(center.dx,
          center.dy - (1 - charge.progress) * 72);
      canvas.drawLine(p, center, Paint()..color =
          const Color(0x79FFEF8B)..strokeWidth = 1.3);
      canvas.drawCircle(p, 6 + (1 - charge.progress) * 3,
          Paint()..color = Palette.primary);
      canvas.drawCircle(center, 4, Paint()..color = const Color(0x99FFDF70));
    }
    for (final ring in rings) {
      final fade = (ring.life / .64).clamp(0.0, 1.0);
      canvas.drawCircle(pt(ring.x, ring.y),
          (ring.radius * (1.18 - fade * .35)) * unit,
          Paint()..color = ring.color.withValues(alpha: fade * .8)
            ..style = PaintingStyle.stroke..strokeWidth = 2.4);
    }
    for (final bullet in shots) {
      final pos = pt(bullet.x, bullet.y);
      canvas.drawCircle(pos, 5.2, Paint()..color = const Color(0x65FF5158));
      canvas.drawCircle(pos, 2.8, Paint()..color = const Color(0xFFFF8D75));
    }
    for (final pickup in pickups) {
      final pos = pt(pickup.x, pickup.y);
      final glow = math.sin(time * 5 + pickup.x * 10) * 2;
      final color = switch(pickup.kind) {
        0 => const Color(0xFFFF7287),
        1 => const Color(0xFF55EFD8),
        2 => const Color(0xFFFFDF68),
        _ => const Color(0xFF9EA7FF),
      };
      canvas.drawCircle(pos, 19 + glow,
          Paint()..color = color.withValues(alpha: .14));
      canvas.drawCircle(pos, 16,
          Paint()..color = color..strokeWidth = 1.3
            ..style = PaintingStyle.stroke);
      final text = switch(pickup.kind) {
        0 => '+', 1 => '⬡', 2 => '✦', _ => '2',
      };
      _label(canvas, text, pos, 18, color, FontWeight.w900);
    }
    final drone = pt(player.dx, player.dy);
    // Horizontal/vertical visual range is approximate and purely fictional.
    canvas.drawCircle(drone, range * unit,
        Paint()..color = Palette.primary.withValues(alpha: .13)
          ..style = PaintingStyle.stroke..strokeWidth = 1.1);
    if (target != null) {
      final p = pt(target!.x, target!.y);
      canvas.drawCircle(p, 20 + math.sin(time * 7) * 2,
          Paint()..color = Palette.primary
            ..style = PaintingStyle.stroke..strokeWidth = 1.4);
      canvas.drawLine(drone, p,
          Paint()..color = const Color(0x58FFDE19)..strokeWidth = 1);
    }
    _drone(canvas, drone, model, time,
        opacity: invulnerable && (time * 13).floor().isEven ? .38 : 1);
    if (shield) canvas.drawCircle(drone, 33,
        Paint()..color = const Color(0xFF70F2D8)
          ..style = PaintingStyle.stroke..strokeWidth = 2.0);
  }
  void _label(Canvas canvas, String text, Offset center, double size,
      Color color, FontWeight weight) {
    final tp = TextPainter(text: TextSpan(text: text,
      style: TextStyle(color: color, fontSize: size, fontWeight: weight)),
      textDirection: TextDirection.ltr, maxLines: 1)..layout();
    tp.paint(canvas, center - Offset(tp.width / 2, tp.height / 2));
  }
  void _groundVehicle(Canvas canvas, Offset p, _GroundTarget e) {
    final tint = switch (e.kind) {
      0 => const Color(0xFFD6AA7D),
      1 => const Color(0xFFB9A887),
      2 => const Color(0xFFD18C70),
      _ => const Color(0xFFFFA175),
    };
    canvas.save(); canvas.translate(p.dx, p.dy);
    canvas.drawOval(const Rect.fromLTWH(-17, -18, 34, 39),
        Paint()..color = const Color(0x68000000));
    if (e.kind == 3) {
      canvas.drawCircle(Offset.zero, 17, Paint()..color = const Color(0xFF38494D));
      canvas.drawCircle(Offset.zero, 13,
          Paint()..color = tint..style = PaintingStyle.stroke..strokeWidth = 3);
      canvas.drawLine(Offset.zero, const Offset(0, -17),
          Paint()..color = tint..strokeWidth = 5..strokeCap = StrokeCap.round);
    } else {
      final w = e.kind == 2 ? 30.0 : e.kind == 1 ? 25.0 : 20.0;
      final h = e.kind == 2 ? 38.0 : e.kind == 1 ? 35.0 : 29.0;
      canvas.drawRRect(RRect.fromRectAndRadius(
          Rect.fromCenter(center: Offset.zero, width: w, height: h),
          const Radius.circular(5)), Paint()..color = tint);
      canvas.drawRRect(RRect.fromRectAndRadius(
          Rect.fromCenter(center: const Offset(0, -4),
              width: w * .67, height: h * .35), const Radius.circular(3)),
          Paint()..color = const Color(0xFF3E5759));
      for (final side in [-1.0, 1.0]) {
        canvas.drawRRect(RRect.fromRectAndRadius(
          Rect.fromCenter(center: Offset(side * (w / 2 + 2), 0),
              width: 6, height: h * .62), const Radius.circular(2)),
          Paint()..color = const Color(0xFF172123));
      }
      if (e.kind == 2) {
        canvas.drawCircle(Offset.zero, 7,
            Paint()..color = const Color(0xFF4D615A));
        canvas.drawLine(const Offset(0, 0), const Offset(0, -22),
            Paint()..color = tint..strokeWidth = 4);
      }
    }
    final fraction = (e.hp / e.maxHp).clamp(0.0, 1.0);
    canvas.drawRRect(RRect.fromRectAndRadius(
        const Rect.fromLTWH(-17, -31, 34, 3.5), const Radius.circular(3)),
        Paint()..color = const Color(0xFF3D4546));
    canvas.drawRRect(RRect.fromRectAndRadius(
        Rect.fromLTWH(-17, -31, 34 * fraction, 3.5),
        const Radius.circular(3)), Paint()..color =
          fraction > .5 ? const Color(0xFFFFDE74) : const Color(0xFFFF7469));
    canvas.restore();
  }
  void _drone(Canvas canvas, Offset p, int model, double t,
      {double opacity = 1}) {
    canvas.save(); canvas.translate(p.dx, p.dy);
    final tint = model == 0 ? const Color(0xFFE7CE80) :
        const Color(0xFFFFE35E);
    final paint = Paint()..color = tint.withValues(alpha: opacity)
      ..strokeCap = StrokeCap.round..strokeWidth = model == 0 ? 4 : 5;
    final arm = model == 0 ? 19.0 : 23.0;
    canvas.drawLine(Offset(-arm, -arm * .65), Offset(arm, arm * .65), paint);
    canvas.drawLine(Offset(arm, -arm * .65), Offset(-arm, arm * .65), paint);
    for (final x in [-arm, arm]) {
      for (final y in [-arm * .65, arm * .65]) {
        canvas.drawCircle(Offset(x, y),
          6 + math.sin(t * 24 + x) * .9,
          Paint()..color = tint.withValues(alpha: opacity * .73)
            ..style = PaintingStyle.stroke..strokeWidth = 2.4);
      }
    }
    final path = Path()..moveTo(0, -18)..lineTo(model == 0 ? 10 : 14, 4)
      ..lineTo(0, 17)..lineTo(model == 0 ? -10 : -14, 4)..close();
    canvas.drawPath(path, Paint()..color = tint.withValues(alpha: opacity));
    canvas.drawCircle(const Offset(0, 1), 3.2, Paint()..color =
        const Color(0xFF192227));
    canvas.restore();
  }
  @override
  bool shouldRepaint(covariant _BomberPainter oldDelegate) => true;
}

class MissionScreen extends StatefulWidget {
  const MissionScreen({super.key, required this.ukrainian,
      required this.active});
  final bool ukrainian, active;
  @override
  State<MissionScreen> createState() => _MissionScreenState();
}
class _MissionScreenState extends State<MissionScreen> {
  int _selectedModel = 0;
  @override
  Widget build(BuildContext context) {
    final ua = widget.ukrainian;
    return ListView(
      padding: const EdgeInsets.fromLTRB(22, 26, 22, 36),
      children: [
        const Kicker('PG / ARCADE'),
        const SizedBox(height: 14),
        Text(ua ? 'Місія: Бомбер' : 'Mission: Bomber',
          style: const TextStyle(fontSize: 33,
            fontWeight: FontWeight.w900)),
        const SizedBox(height: 9),
        Text(ua ? 'Наземні цілі. Автоматичне скидання. Один палець для керування дроном.' :
            'Ground targets. Automatic drop. One-finger drone controls.',
          style: const TextStyle(color: Palette.secondary,
            height: 1.55, fontSize: 13)),
        const SizedBox(height: 22),
        ClipRRect(borderRadius: BorderRadius.circular(22), child:
          SizedBox(height: 260, child: Stack(fit: StackFit.expand, children: [
            Image.asset('assets/images/luckystrike2.jpg', fit: BoxFit.cover,
              errorBuilder: (_, __, ___) =>
                const ColoredBox(color: Color(0xFF213336))),
            const DecoratedBox(decoration: BoxDecoration(gradient:
              LinearGradient(begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Color(0x55080A0B), Color(0xEA080A0B)]))),
            Center(child: Material(color: Palette.primary,
              shape: const CircleBorder(), child: InkWell(
                customBorder: const CircleBorder(),
                onTap: () => _openGame(context),
                child: const SizedBox(width: 94, height: 94,
                  child: Icon(CupertinoIcons.play_fill,
                    size: 39, color: Palette.background))))),
            Positioned(left: 15, right: 15, bottom: 15,
              child: Text(ua ? 'ПОЧАТИ МІСІЮ' : 'START MISSION',
                textAlign: TextAlign.center, style: const TextStyle(
                fontSize: 11, color: Palette.primary,
                fontWeight: FontWeight.w900, letterSpacing: 1.2))),
          ]))),
        const SizedBox(height: 23),
        Text(ua ? 'Оберіть бомбер' : 'Choose your bomber',
          style: const TextStyle(fontSize: 18,
            fontWeight: FontWeight.w900)),
        const SizedBox(height: 12),
        for (var i = 0; i < 2; i++) Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: Material(
            color: _selectedModel == i ?
                const Color(0xFF292B24) : Palette.surface,
            borderRadius: BorderRadius.circular(16),
            child: InkWell(borderRadius: BorderRadius.circular(16),
              onTap: () => setState(() => _selectedModel = i),
              child: Container(
                padding: const EdgeInsets.all(17),
                decoration: BoxDecoration(borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: _selectedModel == i ?
                    Palette.primary : Palette.border)),
                child: Row(children: [
                  Icon(i == 0 ? CupertinoIcons.airplane :
                    CupertinoIcons.airplane,
                    color: _selectedModel == i ? Palette.primary : Palette.secondary,
                    size: 27),
                  const SizedBox(width: 14),
                  Expanded(child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(i == 0 ? 'Lucky Strike 1.5' : 'Lucky Strike 2',
                        style: const TextStyle(fontWeight: FontWeight.w900,
                          fontSize: 15)),
                      const SizedBox(height: 4),
                      Text(i == 0 ? (ua ? 'Компактна зона ураження · швидкий рух' :
                              'Smaller blast · nimble movement') :
                          (ua ? 'Більша зона ураження · сильніший заряд' :
                              'Wider blast · stronger charge'),
                        style: const TextStyle(color: Palette.secondary,
                          fontSize: 11)),
                    ])),
                  Icon(_selectedModel == i ?
                    CupertinoIcons.checkmark_circle_fill :
                    CupertinoIcons.circle, color: _selectedModel == i ?
                      Palette.primary : Palette.secondary),
                ]),
              ),
            ),
          ),
        ),
        const SizedBox(height: 10),
        Row(children: [
          const Icon(CupertinoIcons.shield_fill,
            color: Palette.primary, size: 19),
          const SizedBox(width: 10),
          Expanded(child: Text(ua ?
            'Бонуси в повітрі: ремонт HP, щит, посилення та нова модель.' :
            'Air pickups: HP repair, shield, boost, and model upgrade.',
            style: const TextStyle(color: Palette.secondary,
              fontSize: 12, height: 1.5))),
        ]),
        const SizedBox(height: 15),
        Text(ua ? 'Усі показники та ефекти — умовні ігрові значення.' :
          'All values and effects are fictional arcade settings.',
          style: const TextStyle(color: Palette.tertiary,
            fontSize: 10)),
      ],
    );
  }
  void _openGame(BuildContext context) {
    HapticFeedback.mediumImpact();
    Navigator.of(context).push(PageRouteBuilder<void>(
      opaque: true,
      transitionDuration: const Duration(milliseconds: 290),
      reverseTransitionDuration: const Duration(milliseconds: 230),
      pageBuilder: (context, _, __) => MissionGameView(
        ukrainian: widget.ukrainian, active: true,
        initialModel: _selectedModel),
      transitionsBuilder: (_, animation, __, child) => SlideTransition(
        position: Tween(begin: const Offset(0, 1), end: Offset.zero)
          .animate(CurvedAnimation(parent: animation,
            curve: Curves.easeOutCubic)), child: child),
    ));
  }
}