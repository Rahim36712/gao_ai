import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';
import 'screen6_dispatch_tracker.dart';

class Screen5ResponsePlan extends StatelessWidget {
  const Screen5ResponsePlan({super.key});

  final List<Map<String, dynamic>> _departments = const [
    {
      'dept': 'DISASTER',
      'team': 'Rescue 1122 - Alpha',
      'icon': Icons.flood,
      'dist': '12.4',
      'eta': '25',
      'id': 'TKT-991',
    },
    {
      'dept': 'HEALTH',
      'team': 'Mobile Med Unit 3',
      'icon': Icons.local_hospital,
      'dist': '8.1',
      'eta': '15',
      'id': 'TKT-992',
    },
    {
      'dept': 'AGRICULTURE',
      'team': 'Crop Assessors Dadu',
      'icon': Icons.agriculture,
      'dist': '45.0',
      'eta': '90',
      'id': 'TKT-993',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Response Plan')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Three departments activated in parallel', style: TextStyle(color: Colors.grey[600], fontStyle: FontStyle.italic)),
            const SizedBox(height: 24),
            
            Expanded(
              child: ListView.builder(
                itemCount: _departments.length,
                itemBuilder: (context, index) {
                  final dept = _departments[index];
                  return _buildDeptCard(context, dept).animate().fadeIn(duration: 500.ms).slideY(begin: 0.2, end: 0);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDeptCard(BuildContext context, Map<String, dynamic> dept) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: AppTheme.primaryNavy.withOpacity(0.2))),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: AppTheme.primaryNavy.withOpacity(0.1),
                  child: Icon(dept['icon'], color: AppTheme.primaryNavy),
                )
                .animate(onPlay: (c) => c.repeat(reverse: true))
                .scale(begin: const Offset(1, 1), end: const Offset(1.1, 1.1), duration: 1.seconds), // Animated pulse
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(dept['dept'], style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.grey, fontSize: 12)),
                      Text(dept['team'], style: Theme.of(context).textTheme.titleMedium),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: Colors.grey[200], borderRadius: BorderRadius.circular(4)),
                  child: Text(dept['id'], style: const TextStyle(fontFamily: 'monospace', fontSize: 12)),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem('Distance', '${dept['dist']} km'),
                _buildStatItem('ETA', '${dept['eta']} min'),
                _buildStatItem('Status', 'ASSIGNED', isStatus: true),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                icon: const Icon(Icons.track_changes),
                label: const Text('Track Live'),
                style: OutlinedButton.styleFrom(foregroundColor: AppTheme.accentBlue, side: const BorderSide(color: AppTheme.accentBlue)),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => Screen6DispatchTracker(initialTicketId: dept['id'])),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, {bool isStatus = false}) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: isStatus ? AppTheme.accentBlue : AppTheme.primaryNavy,
          ),
        ),
      ],
    );
  }
}
