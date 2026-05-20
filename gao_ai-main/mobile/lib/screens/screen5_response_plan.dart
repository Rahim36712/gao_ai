import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';
import 'screen6_dispatch_tracker.dart';

class Screen5ResponsePlan extends StatelessWidget {
  final Map<String, dynamic> analysisResult;
  const Screen5ResponsePlan({super.key, required this.analysisResult});

  IconData _iconFromString(String? icon) {
    switch (icon) {
      case 'flood': return Icons.flood;
      case 'local_hospital': return Icons.local_hospital;
      case 'person_search': return Icons.person_search;
      case 'local_fire_department': return Icons.local_fire_department;
      case 'volunteer_activism': return Icons.volunteer_activism;
      case 'construction': return Icons.construction;
      case 'emergency': return Icons.emergency;
      default: return Icons.groups;
    }
  }

  @override
  Widget build(BuildContext context) {
    final teams = List<Map<String, dynamic>>.from(analysisResult['response_teams'] ?? []);
    final a1 = analysisResult['a1_signals'] as Map<String, dynamic>;
    final location = a1['location_name'] ?? 'Unknown';

    if (teams.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Response Plan')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.check_circle, size: 64, color: AppTheme.successEmerald),
              const SizedBox(height: 16),
              Text('No emergency response needed', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              Text('Situation is under monitor status.', style: TextStyle(color: AppTheme.textSecondary)),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Response Plan')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              '${teams.length} team(s) dispatched to $location in parallel',
              style: TextStyle(color: AppTheme.textSecondary, fontStyle: FontStyle.italic),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: teams.length,
                itemBuilder: (context, index) {
                  final dept = teams[index];
                  return Card(
                    margin: const EdgeInsets.only(bottom: 16),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              CircleAvatar(
                                backgroundColor: AppTheme.accentBlue.withValues(alpha: 0.15),
                                child: Icon(_iconFromString(dept['icon']), color: AppTheme.accentBlue),
                              ).animate(onPlay: (c) => c.repeat(reverse: true))
                               .scale(begin: const Offset(1, 1), end: const Offset(1.08, 1.08), duration: 1.5.seconds),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      dept['dept'] ?? '',
                                      style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textSecondary, fontSize: 11),
                                    ),
                                    Text(dept['team'] ?? '', style: Theme.of(context).textTheme.titleMedium),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AppTheme.cardDark,
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  dept['id'] ?? '',
                                  style: const TextStyle(fontFamily: 'monospace', fontSize: 12, color: AppTheme.accentCyan),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              _statItem('Distance', '${dept['dist']} km'),
                              _statItem('ETA', '${dept['eta']} min'),
                              _statItem('Status', 'ASSIGNED', isStatus: true),
                            ],
                          ),
                          const SizedBox(height: 12),
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton.icon(
                              icon: const Icon(Icons.track_changes),
                              label: const Text('Track Live'),
                              style: OutlinedButton.styleFrom(
                                foregroundColor: AppTheme.accentCyan,
                                side: const BorderSide(color: AppTheme.accentCyan),
                              ),
                              onPressed: () => Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => Screen6DispatchTracker(initialTicketId: dept['id'] ?? 'TKT-900'),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ).animate().fadeIn(delay: Duration(milliseconds: index * 200)).slideY(begin: 0.2);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statItem(String label, String value, {bool isStatus = false}) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
            color: isStatus ? AppTheme.accentCyan : AppTheme.textPrimary,
          ),
        ),
      ],
    );
  }
}
