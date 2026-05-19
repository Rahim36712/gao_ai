import 'package:flutter_test/flutter_test.dart';
import 'package:gaon_guard_mobile/main.dart';

void main() {
  testWidgets('App renders', (WidgetTester tester) async {
    await tester.pumpWidget(const GaonGuardApp());
    expect(find.text('Gaon Guard AI'), findsOneWidget);
  });
}
