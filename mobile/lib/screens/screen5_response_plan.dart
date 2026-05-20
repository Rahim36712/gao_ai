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
        appBar: AppBar(
          title: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Help on the Way', style: TextStyle(fontSize: 18)),
              Text('مدد آ رہی ہے', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
            ],
          ),
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.check_circle, size: 64, color: AppTheme.successEmerald),
              const SizedBox(height: 16),
              Text('No emergency response needed', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 4),
              const Text('ہنگامی ردعمل کی ضرورت نہیں', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
              const SizedBox(height: 8),
              Text('Situation is being monitored.', style: TextStyle(color: AppTheme.textSecondary)),
              const Text('صورتحال زیر نگرانی ہے', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Help on the Way', style: TextStyle(fontSize: 18)),
            Text('مدد آ رہی ہے', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
          ],
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              '${teams.length} team(s) heading to $location',
              style: const TextStyle(color: AppTheme.textPrimary, fontWeight: FontWeight.w600, fontSize: 15),
            ),
            Text(
              '${teams.length} ٹیمیں $location کی طرف جا رہی ہیں',
              style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: teams.length,
                itemBuilder: (context, index) {
                  final dept = teams[index];
                  final dist = dept['dist'];
                  final eta = dept['eta'];
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
                            ],
                          ),
                          const SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              _statItem('$dist km away', '$dist کلومیٹر دور'),
                              _statItem('Arriving in ~$eta min', 'تقریباً $eta منٹ'),
                            ],
                          ),
                          const SizedBox(height: 12),
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton.icon(
                              icon: const Icon(Icons.track_changes),
                              label: const Column(
                                children: [
                                  Text('Track Team'),
                                  Text('ٹیم ٹریک کریں', style: TextStyle(fontSize: 10)),
                                ],
                              ),
                              style: OutlinedButton.styleFrom(
                                foregroundColor: AppTheme.accentCyan,
                                side: const BorderSide(color: AppTheme.accentCyan),
                                padding: const EdgeInsets.symmetric(vertical: 12),
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

  Widget _statItem(String english, String urdu) {
    return Column(
      children: [
        Text(
          english,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          urdu,
          style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
        ),
      ],
    );
  }
}
