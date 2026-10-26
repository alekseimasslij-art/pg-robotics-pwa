import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:pg_robotics_app/mission_game.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('iPhone bomber HUD remains visible and back button exits',
      (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(MaterialApp(home: Scaffold(
      body: Center(child: ElevatedButton(
        onPressed: () => Navigator.of(tester.element(find.text('Start')))
            .push(MaterialPageRoute<void>(
              builder: (_) => const MissionGameView(
                ukrainian: true, active: true))),
        child: const Text('Start'),
      )),
    )));
    await tester.tap(find.text('Start'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 260));

    expect(find.text('BOMBER'), findsWidgets);
    expect(find.textContaining('HP '), findsOneWidget);
    expect(find.textContaining('РАХУНОК'), findsOneWidget);
    expect(find.textContaining('РЕКОРД'), findsOneWidget);
    expect(find.textContaining('ХВИЛЯ'), findsOneWidget);
    expect(find.byTooltip('До меню'), findsOneWidget);
    expect(find.byTooltip('Пауза'), findsOneWidget);

    final exit = find.byTooltip('До меню');
    final bounds = tester.getRect(exit);
    expect(bounds.top, greaterThanOrEqualTo(0));
    expect(bounds.bottom, lessThanOrEqualTo(844));
    await tester.tap(exit);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('Start'), findsOneWidget);
  });
}
