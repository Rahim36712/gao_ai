import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';

class Screen10BeforeAfter extends StatelessWidget {
  const Screen10BeforeAfter({super.key});

  final List<Map<String, String>> _comparisons = const [
    {
      'topic': 'Complaint processing',
      'before': 'Manual reading, language barriers, hours of delay.',
      'after': 'Instant parsing (A1), multlingual support, structured JSON.',
    },
    {
      'topic': 'Evidence verification',
      'before': 'Phone calls to local officials, anecdotal, slow.',
      'after': 'Agent A2 checks 5 APIs in parallel in under 2 seconds.',
    },
    {
      'topic': 'Severity',
      'before': 'Subjective guessing, prone to bias.',
      'after': 'Agent A3 applies weighted scoring logic objectively.',
    },
    {
      'topic': 'Dispatch',
      'before': 'Radio calls, chaotic assignment.',
      'after': 'Agent A4 uses Haversine math, assigns nearest teams.',
    },
    {
      'topic': 'Missing persons',
      'before': 'Paper lists, delayed matching across camps.',
      'after': 'B1-B3 scan actively, score matches, detect clusters.',
    },
    {
      'topic': 'Aid accountability',
      'before': 'Post-disaster audits months later, high fraud.',
      'after': 'C1-C3 run real-time anomaly detection, flag fraud live.',
    },
    {
      'topic': 'Conflict handling',
      'before': 'Ignored data, conflicting reports cause paralysis.',
      'after': 'Agent X (Coordinator) arbitrates and justifies holds.',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Impact of Agentic Response')),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Expanded(child: Text('Before Gaon Guard AI', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textSecondary))),
                      const SizedBox(width: 16),
                      const Expanded(child: Text('After Gaon Guard AI', textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryNavy))),
                    ],
                  ),
                  const Divider(height: 32),
                  ..._comparisons.map((c) => _buildComparisonRow(c)).toList(),
                ],
              ),
            ),
          ),
          
          // Live Stats Footer
          Container(
            padding: const EdgeInsets.all(16),
            color: AppTheme.primaryNavy,
            child: const SafeArea(
              top: false,
              child: Text(
                'Active crisis events: 4 | Tickets dispatched: 12 | Missing cases: 3 | Audit flags: 2',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ),
          ).animate().slideY(begin: 1, end: 0, duration: 800.ms),
        ],
      ),
    );
  }

  Widget _buildComparisonRow(Map<String, String> data) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(data['topic']!, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey), textAlign: TextAlign.center),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(color: Colors.red.shade50, borderRadius: BorderRadius.circular(8)),
                  child: Column(
                    children: [
                      const Icon(Icons.close, color: AppTheme.alertCrimson, size: 20),
                      const SizedBox(height: 4),
                      Text(data['before']!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12, color: AppTheme.textPrimary)),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(color: AppTheme.successEmerald.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                  child: Column(
                    children: [
                      const Icon(Icons.check_circle, color: AppTheme.successEmerald, size: 20),
                      const SizedBox(height: 4),
                      Text(data['after']!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12, color: AppTheme.primaryNavy)),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ).animate().fadeIn().slideY(begin: 0.1, end: 0),
    );
  }
}
