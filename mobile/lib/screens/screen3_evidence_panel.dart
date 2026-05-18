import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';
import 'screen4_severity_dashboard.dart';

class Screen3EvidencePanel extends StatefulWidget {
  const Screen3EvidencePanel({super.key});

  @override
  State<Screen3EvidencePanel> createState() => _Screen3EvidencePanelState();
}

class _Screen3EvidencePanelState extends State<Screen3EvidencePanel> {
  final List<Map<String, dynamic>> _evidenceItems = [
    {
      'source': 'Rainfall Data',
      'value': '0mm in last 24h',
      'verdict': 'CONTRADICTS',
      'justification': 'Weather data shows 0mm rainfall but complaint claims flooding.',
      'icon': Icons.water_drop,
    },
    {
      'source': 'Road Status',
      'value': 'Blocked',
      'verdict': 'SUPPORTS',
      'justification': 'Main road to Ali Pur is confirmed blocked, consistent with flood claim.',
      'icon': Icons.add_road,
    },
    {
      'source': 'Health Reports',
      'value': 'Diarrhea Cases: 12',
      'verdict': 'SUPPORTS',
      'justification': 'Health spike supports contaminated water from flooding.',
      'icon': Icons.local_hospital,
    },
    {
      'source': 'Crop Calendar',
      'value': 'Harvest Season',
      'verdict': 'NEUTRAL',
      'justification': 'Harvest season is ongoing, neither confirms nor denies flooding.',
      'icon': Icons.grass,
    },
    {
      'source': 'Nearby Reports',
      'value': 'Missing Child Reported',
      'verdict': 'SUPPORTS',
      'justification': 'Missing person report corroborates crisis in area.',
      'icon': Icons.campaign,
    },
  ];

  int _visibleCount = 0;
  bool _showConfidence = false;

  @override
  void initState() {
    super.initState();
    _animateEvidence();
  }

  Future<void> _animateEvidence() async {
    for (int i = 0; i < _evidenceItems.length; i++) {
      await Future.delayed(const Duration(milliseconds: 500));
      if (!mounted) return;
      setState(() => _visibleCount = i + 1);
    }
    await Future.delayed(const Duration(milliseconds: 500));
    if (!mounted) return;
    setState(() => _showConfidence = true);
  }

  Widget _buildVerdictBadge(String verdict) {
    Color color;
    switch (verdict) {
      case 'SUPPORTS': color = AppTheme.successEmerald; break;
      case 'CONTRADICTS': color = AppTheme.alertCrimson; break;
      default: color = Colors.grey; break;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(4)),
      child: Text(verdict, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }

  @override
  Widget build(BuildContext context) {
    bool hasConflict = _evidenceItems.take(_visibleCount).any((e) => e['verdict'] == 'CONTRADICTS');

    return Scaffold(
      appBar: AppBar(title: const Text('Evidence Verification')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Agent A2 checking 5 data sources', style: TextStyle(color: Colors.grey[600], fontStyle: FontStyle.italic)),
            const SizedBox(height: 16),
            
            ...List.generate(_evidenceItems.length, (index) {
              if (index >= _visibleCount) return const SizedBox.shrink();
              final item = _evidenceItems[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ExpansionTile(
                  leading: Icon(item['icon'], color: AppTheme.primaryNavy),
                  title: Text(item['source'], style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(item['value']),
                  trailing: _buildVerdictBadge(item['verdict']),
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(item['justification'], style: TextStyle(color: Colors.grey[700])),
                    ),
                  ],
                ),
              ).animate().fadeIn().slideX();
            }),

            if (_showConfidence) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppTheme.primaryNavy,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Column(
                  children: [
                    Text('Confidence Level', style: TextStyle(color: Colors.white70)),
                    SizedBox(height: 4),
                    Text('MEDIUM', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
                  ],
                ),
              ).animate().fadeIn().scale(),
            ],

            if (hasConflict) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(color: Colors.orange.shade100, borderRadius: BorderRadius.circular(8), border: Border.all(color: Colors.orange)),
                child: Row(
                  children: [
                    const Icon(Icons.warning_amber_rounded, color: Colors.deepOrange),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text(
                        'Conflict detected — Coordinator Agent X reviewing',
                        style: TextStyle(color: Colors.orange.shade900, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn(),
            ],

            const SizedBox(height: 32),
            if (_showConfidence)
              ElevatedButton(
                onPressed: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => const Screen4SeverityDashboard()),
                  );
                },
                child: const Text('Continue to Severity Dashboard'),
              ).animate().fadeIn(),
          ],
        ),
      ),
    );
  }
}
