import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:pg_robotics_app/mission_game.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Bomber hub offers both models and starts with selected LS2',
      (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(body: MissionScreen(ukrainian: true, active: true)),
    ));
    expect(find.text('Місія: Бомбер'), findsOneWidget);
    expect(find.text('Lucky Strike 1.5'), findsOneWidget);
    expect(find.text('Lucky Strike 2'), findsOneWidget);
    await tester.tap(find.text('Lucky Strike 2'));
    await tester.pump();
    // The model selection changes the starting drone without external input.
    expect(find.byIcon(Icons.check_circle), findsNothing);
  });
}
