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
      theme: AppTheme.lightTheme,
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
    const Screen1CrisisInput(), // Crisis Tab
    const Screen7MissingPersons(), // Missing Tab
    const Screen8AidDistribution(), // Aid Tab
    const Screen9AgentTraceViewer(), // Trace Tab
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Gaon Guard AI'),
        actions: [
          TextButton.icon(
            icon: const Icon(Icons.compare_arrows, color: Colors.white),
            label: const Text('Before vs After', style: TextStyle(color: Colors.white)),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const Screen10BeforeAfter()),
              );
            },
          ),
        ],
      ),
      body: DemoBannerWrapper(
        child: IndexedStack(
          index: _currentIndex,
          children: _pages,
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: AppTheme.accentBlue,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.warning_amber_rounded), label: 'Crisis'),
          BottomNavigationBarItem(icon: Icon(Icons.person_search), label: 'Missing'),
          BottomNavigationBarItem(icon: Icon(Icons.inventory_2), label: 'Aid'),
          BottomNavigationBarItem(icon: Icon(Icons.analytics), label: 'Trace'),
        ],
      ),
    );
  }
}
