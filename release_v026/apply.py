from pathlib import Path
import math

def fix(path,a,b):
 p=Path(path);s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(path+': pattern missing / duplicated: '+a[:95])
 p.write_text(s.replace(a,b))

p=Path('lib/mission_game.dart');s=p.read_text()
def rep(a,b):
 global s
 if s.count(a)!=1:raise RuntimeError('game: '+a[:110]+' count '+str(s.count(a)))
 s=s.replace(a,b)

rep('final double startX, startY, x, y, radius, power;\n  final bool ultimate;',
    'final double startX, startY, radius, power;\n  double x, y;\n  final _GroundTarget? victim;\n  final bool ultimate;')
rep('this.radius, this.power, {this.ultimate = false});',
    'this.radius, this.power, {this.ultimate = false,this.victim});')
rep('class _AirPickup {',
    'class _Wreck {\n  _Wreck(this.x,this.y,this.kind);\n  double x,y;\n  final int kind;\n}\nclass _AirPickup {')
rep('final List<_WorldObject> _world = [];',
    'final List<_WorldObject> _world = [];\n  final List<_Wreck> _wrecks = [];')
rep('double _ultimate = 0, _damageFlash = 0, _upgradeClock = 0;',
    'double _ultimate = 0, _damageFlash = 0, _upgradeClock = 0, _enhanced = 0;')
rep('_pickups.clear(); _rings.clear(); _world.clear();',
    '_pickups.clear(); _rings.clear(); _world.clear(); _wrecks.clear();')
rep('_hudClock = 0; _ultimate = 0; _damageFlash = 0;',
    '_hudClock = 0; _ultimate = 0; _damageFlash = 0; _enhanced=0;')
rep('final baseHp = switch(kind) {1 => 3.7, 2 => 5.8,\n      3 => 4.2, 6 => 2.8, _ => 2.1};\n    final hp = baseHp * (1.0 + (_wave - 1) * .16);',
    'final baseHp = switch(kind) {1 => 2.0, 2 => 3.25,\n      3 => 2.45, 6 => 1.18, _ => .90};\n    final hp = baseHp * (1.0 + math.min(1.3,(_wave-1)*.055));')
rep('final y = (target.y + target.velocity * .53).clamp(.035, .97).toDouble();',
    'final y = target.y;')
rep('_blastRadius, _blastPower));','_blastRadius, _blastPower, victim:target));')
rep('if (target.hp <= 0) {\n        _targets.remove(target);',
    'if (target.hp <= 0) {\n        _targets.remove(target);\n        _wrecks.add(_Wreck(target.x,target.y,target.kind));\n        if(_wrecks.length>32)_wrecks.removeAt(0);')
rep('_ultimate = 0;\n    final focus = _nearestTarget();',
    '_ultimate = 0;\n    _enhanced=16;\n    _boost=math.max(_boost,16);\n    final focus = _nearestTarget();')
rep("_showFlash(widget.ukrainian ? 'УЛЬТА · ШИРОКА ХВИЛЯ' : 'ULTIMATE · SHOCKWAVE', 1.8);",
    "_showFlash(widget.ukrainian ? 'ПОСИЛЕННЯ · 16 СЕКУНД' : 'ENHANCED · 16 SECONDS', 2.2);")
rep('for (final item in _world) { item.y += dt * landscapeSpeed; }',
    'for (final item in _world) { item.y += dt * landscapeSpeed; }\n    for (final w in _wrecks) {w.y += dt * landscapeSpeed;}\n    _wrecks.removeWhere((w)=>w.y>1.15);')
rep('_ultimate = math.min(1.0, _ultimate + dt / 68);',
    '_ultimate = math.min(1.0, _ultimate + dt / 68);\n    _enhanced=math.max(0,_enhanced-dt);')
rep('charge.progress += dt / (charge.ultimate ? 1.05 : .87);\n      if (charge.progress >= 1)',
    'charge.progress += dt / (charge.ultimate ? .66 : .45);\n      if(charge.victim!=null && _targets.contains(charge.victim)){\n        charge.x=charge.victim!.x;charge.y=charge.victim!.y;\n      }\n      if (charge.progress >= 1)')
rep("Text(_ultimate>=1?(ua?'УЛЬТА · АКТИВУВАТИ':'ULTIMATE · ACTIVATE'):\n                    '${ua?'УЛЬТА':'ULTIMATE'}  ${(_ultimate*100).floor()}%',",
    "Text(_enhanced>0?'${ua?'ПОСИЛЕННЯ':'ENHANCED'} ${_enhanced.ceil()} c':\n                    _ultimate>=1?(ua?'ПОСИЛЕНА · УВІМКНУТИ':'ENHANCED · ACTIVATE'):\n                    '${ua?'ПОСИЛЕНА':'ENHANCED'}  ${(_ultimate*100).floor()}%',")
rep('target: _nearestTarget(),','target: _nearestTarget(),wrecks:_wrecks,')
rep('required this.range, required this.blast, required this.target});',
    'required this.range, required this.blast, required this.target, required this.wrecks});')
rep('final List<_WorldObject> world;',
    'final List<_WorldObject> world;\n  final List<_Wreck> wrecks;')
rep('_terrain(canvas, size);\n    final unit',
    """_terrain(canvas, size);
    for(final w in wrecks){
      final p=Offset(w.x*size.width,w.y*size.height);
      canvas.drawOval(Rect.fromCenter(center:p,width:w.kind==5?58:35,height:w.kind==5?30:18),
        Paint()..color=const Color(0xFF27292A));
      canvas.drawOval(Rect.fromCenter(center:p.translate(0,-2),width:w.kind==5?40:24,height:w.kind==5?20:10),
        Paint()..color=const Color(0xFF4C4339));
      canvas.drawLine(p.translate(-11,-4),p.translate(11,6),
        Paint()..color=const Color(0xFF80705B)..strokeWidth=2);
    }
    final unit""")
rep("Text(ua ? 'БОМБЕР · АВТОСКИДАННЯ' : 'BOMBER · AUTO DROP',",
    "Text(ua ? 'ГРА · BOMBER' : 'GAME · BOMBER',")
rep("Align(alignment:Alignment.centerLeft,child:Text('АГРА БОМБЕР',",
    "Align(alignment:Alignment.centerLeft,child:Text('ГРА · BOMBER',")
rep("Text(_finished ? '${ua ? 'Результат' : 'Score'}: $_score' :\n                        (ua ? 'Один палець — рух дрона. Скидання автоматичне.' :\n                            'One finger moves the drone. Drops are automatic.'),",
    "Text(_finished ? '${ua ? 'Результат' : 'Score'}: $_score' :\n                        (ua ? 'Гра призупинена' : 'Game paused'),")
start=s.index('          Positioned(left:15,right:15,bottom:18,child:Row(children:[')
end=s.index('        ]))),',start)
s=s[:start]+"""          Positioned(left:18,right:18,bottom:28,child:Column(children:[
            Text(ua?'Керуйте дроном і зупиняйте цілі':'Pilot the drone and stop targets',
              textAlign:TextAlign.center,style:const TextStyle(fontSize:16,
                fontWeight:FontWeight.w800,color:Colors.white)),
            const SizedBox(height:6),
            Text(ua?'Один палець · автоматичне скидання · підсилення':
              'One finger · automatic drops · power-ups',
              textAlign:TextAlign.center,style:const TextStyle(fontSize:11,color:Colors.white70)),
          ])),
""" +s[end:]
p.write_text(s)
fix('lib/main.dart',"localized(ukrainian, 'Місія Агра', 'Agra Mission')",
    "localized(ukrainian, 'Гра', 'Game')")
fix('lib/drone_viewer_web.dart',
    "'&specs=${Uri.encodeComponent(widget.specs)}'",
    "'&specs=${Uri.encodeComponent(widget.specs)}'\n      '&modelId=${Uri.encodeComponent(widget.id)}'")
fix('pubspec.yaml','version: 0.25.0+25','version: 0.26.0+26')

p=Path('deploy/pg_model_viewer.html');x=p.read_text()
def rep3(a,b):
 global x
 if x.count(a)!=1:raise RuntimeError('viewer: '+a[:85])
 x=x.replace(a,b)
rep3("pointer-events:none;display:none;line-height:1.15}",
     "pointer-events:auto;display:none;line-height:1.15}")
rep3("#specs .spec-head{color:#ffde19;font-size:9px;font-weight:800;letter-spacing:1.2px;margin-bottom:8px}",
     "#specs .spec-head{display:flex;align-items:center;justify-content:space-between;gap:9px;color:#ffde19;font-size:9px;font-weight:800;letter-spacing:1px;margin-bottom:8px}#specs button{border:1px solid #777;background:#34383a;color:#ffde19;border-radius:7px;width:32px;height:29px;cursor:pointer;font-size:15px;touch-action:manipulation}#specs.collapsed{width:auto;padding:5px 8px}#specs.collapsed .spec-row{display:none}#specs.collapsed .spec-head{margin:0}")
rep3("const selection=document.getElementById('modelSelect');",
     "const selection=document.getElementById('modelSelect');let specsCollapsed=false;")
rep3("option.textContent=item.name;option.selected=item.id===params.get('id');selection.append(option);",
     "option.textContent=item.name;option.selected=item.id===params.get('modelId');selection.append(option);")
rep3("const header=document.createElement('div');header.className='spec-head';header.textContent='ТТХ · ПОРІВНЯННЯ';specEl.append(header);",
     """const header=document.createElement('div');header.className='spec-head';
  const label=document.createElement('span');label.textContent='ТТХ';
  const eye=document.createElement('button');eye.type='button';
  eye.textContent='👁';
  eye.title=specsCollapsed?'Показати ТТХ':'Сховати ТТХ';
  eye.setAttribute('aria-label',eye.title);
  eye.addEventListener('pointerdown',ev=>ev.stopPropagation());
  eye.addEventListener('click',ev=>{
    ev.preventDefault();ev.stopPropagation();specsCollapsed=!specsCollapsed;
    specEl.classList.toggle('collapsed',specsCollapsed);
    eye.textContent='👁';
    eye.title=specsCollapsed?'Показати ТТХ':'Сховати ТТХ';
    eye.setAttribute('aria-label',eye.title);
  });
  header.append(label,eye);specEl.append(header);
  specEl.classList.toggle('collapsed',specsCollapsed);""")
p.write_text(x)
print('v0.26 patch complete')
