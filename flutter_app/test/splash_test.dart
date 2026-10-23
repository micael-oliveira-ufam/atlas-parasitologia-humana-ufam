import 'package:atlas_parasitologia/ui/splash.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('SplashView mostra o título e anima sem lançar exceção', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: SplashView()));
    await tester.pump(const Duration(milliseconds: 1000));
    expect(find.text('Atlas de Parasitologia'), findsOneWidget);
    expect(find.text('Parasitologia Humana'), findsOneWidget);
    expect(find.text('Universidade Federal do Amazonas'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
