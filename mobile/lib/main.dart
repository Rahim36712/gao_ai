import 'package:flutter/material.dart';
import 'package:gaon_guard_mobile/screens/screen1_crisis_input.dart';
import 'package:gaon_guard_mobile/screens/screen7_missing_persons.dart';
import 'package:gaon_guard_mobile/screens/screen8_aid_distribution.dart';
import 'package:gaon_guard_mobile/screens/screen9_agent_trace_viewer.dart';
import 'package:gaon_guard_mobile/screens/screen10_before_after.dart';
import 'package:gaon_guard_mobile/theme.dart';

void main() {
  runApp(const GaonGuardApp());
}

class GaonGuardApp extends StatelessWidget {
  const GaonGuardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Gaon Guard AI',
      theme: AppTheme.darkTheme,
      home: const MainNavigator(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MainNavigator extends StatefulWidget {
  const MainNavigator({super.key});

  @override
  State<MainNavigator> createState() => _MainNavigatorState();
}

class _MainNavigatorState extends State<MainNavigator> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const Screen1CrisisInput(),
    const Screen7MissingPersons(),
    const Screen8AidDistribution(),
    const Screen9AgentTraceViewer(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.accentBlue, AppTheme.accentCyan],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.shield, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 10),
            const Text('Gaon Guard AI'),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 8),
            child: TextButton.icon(
              icon: const Icon(Icons.compare_arrows, color: AppTheme.accentCyan, size: 18),
              label: Text('Before vs After',
                  style: TextStyle(color: AppTheme.accentCyan, fontSize: 13)),
              style: TextButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                  side: BorderSide(color: AppTheme.accentCyan.withOpacity(0.3)),
                ),
              ),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const Screen10BeforeAfter()),
                );
              },
            ),
          ),
        ],
      ),
      body: DemoBannerWrapper(
        child: IndexedStack(
          index: _currentIndex,
          children: _pages,
        ),
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          border: Border(
            top: BorderSide(color: AppTheme.textSecondary.withOpacity(0.1)),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) => setState(() => _currentIndex = index),
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.warning_amber_rounded), label: 'Crisis'),
            BottomNavigationBarItem(icon: Icon(Icons.person_search), label: 'Missing'),
            BottomNavigationBarItem(icon: Icon(Icons.inventory_2), label: 'Aid'),
            BottomNavigationBarItem(icon: Icon(Icons.analytics), label: 'Traces'),
          ],
        ),
      ),
    );
  }
}
