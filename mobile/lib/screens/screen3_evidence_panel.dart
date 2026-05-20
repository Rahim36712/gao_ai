import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';
import 'screen4_severity_dashboard.dart';

class Screen3EvidencePanel extends StatefulWidget {
  final Map<String, dynamic> analysisResult;
  const Screen3EvidencePanel({super.key, required this.analysisResult});

  @override
  State<Screen3EvidencePanel> createState() => _Screen3EvidencePanelState();
}

class _Screen3EvidencePanelState extends State<Screen3EvidencePanel> {
  bool _showConfidence = false;

  late final List<Map<String, dynamic>> _evidenceItems;
  late final String _confidence;
  late final bool _hasConflict;

  @override
  void initState() {
    super.initState();
    final a2 = widget.analysisResult['a2_evidence'] as Map<String, dynamic>;
    _confidence = a2['confidence'] ?? 'MEDIUM';
    _hasConflict = a2['has_conflict'] == true;
    _evidenceItems =
        List<Map<String, dynamic>>.from(a2['evidence_checks'] ?? []);

    // Show confidence after a brief delay (no progressive reveal)
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted) setState(() => _showConfidence = true);
    });
  }

  Widget _buildVerdictBadge(String verdict) {
    final config = {
      'SUPPORTS': (AppTheme.successEmerald, '✅ Confirmed / تصدیق'),
      'CONTRADICTS': (AppTheme.alertCrimson, '⚠️ Mismatch / تضاد'),
      'NEUTRAL': (AppTheme.textSecondary, 'ℹ️ Checking / جانچ'),
    };
    final (color, label) = config[verdict] ?? (AppTheme.textSecondary, verdict);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
          color: color, borderRadius: BorderRadius.circular(6)),
      child: Text(label,
          style: const TextStyle(
              color: Colors.white,
              fontSize: 10,
              fontWeight: FontWeight.bold)),
    );
  }

  IconData _sourceIcon(String source) {
    if (source.contains('Rain') || source.contains('Weather')) {
      return Icons.water_drop;
    }
    if (source.contains('Road')) return Icons.add_road;
    if (source.contains('Health')) return Icons.local_hospital;
    if (source.contains('Crop') || source.contains('Calendar')) {
      return Icons.grass;
    }
    if (source.contains('Missing') || source.contains('Nearby')) {
      return Icons.campaign;
    }
    return Icons.analytics;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Verifying Report', style: TextStyle(fontSize: 18)),
            Text('رپورٹ کی تصدیق',
                style:
                    TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header – bilingual
            const Text(
              'Verifying information...',
              style: TextStyle(
                  color: AppTheme.textSecondary, fontStyle: FontStyle.italic),
            ),
            const Text(
              'معلومات کی تصدیق',
              style: TextStyle(fontSize: 12, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 16),

            // Evidence items – all shown immediately, each with fadeIn
            ...List.generate(_evidenceItems.length, (i) {
              final item = _evidenceItems[i];
              final verdict = item['verdict'] as String? ?? 'NEUTRAL';
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ExpansionTile(
                  leading: Icon(_sourceIcon(item['source'] ?? ''),
                      color: AppTheme.accentCyan),
                  title: Text(item['source'] ?? '',
                      style:
                          const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(item['value'] ?? ''),
                  trailing: _buildVerdictBadge(verdict),
                  children: [
                    Padding(
                      padding:
                          const EdgeInsets.fromLTRB(16, 0, 16, 12),
                      child: Text(
                        item['justification'] ?? '',
                        style: const TextStyle(
                            color: AppTheme.textSecondary, height: 1.4),
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn(delay: Duration(milliseconds: 100 * i)).slideX(begin: 0.05);
            }),

            // Conflict warning – bilingual
            if (_hasConflict) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppTheme.warningAmber.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppTheme.warningAmber),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.warning_amber_rounded,
                            color: AppTheme.warningAmber),
                        SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            '⚠️ Some information doesn\'t match — checking further',
                            style: TextStyle(
                                color: AppTheme.warningAmber,
                                fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 4),
                    Padding(
                      padding: EdgeInsets.only(left: 36),
                      child: Text(
                        'معلومات میل نہیں کھاتیں',
                        style: TextStyle(
                            color: AppTheme.warningAmber, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn(),
            ],

            // Confidence + Continue button – shown immediately
            if (_showConfidence) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: _confidence == 'HIGH'
                        ? [AppTheme.successEmerald, const Color(0xFF059669)]
                        : _confidence == 'MEDIUM'
                            ? [
                                AppTheme.warningAmber,
                                const Color(0xFFD97706)
                              ]
                            : [
                                AppTheme.alertCrimson,
                                const Color(0xFFDC2626)
                              ],
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    const Text('Evidence Confidence',
                        style: TextStyle(
                            color: Colors.white70, fontSize: 13)),
                    const SizedBox(height: 4),
                    Text(_confidence,
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 28,
                            fontWeight: FontWeight.bold)),
                  ],
                ),
              ).animate().fadeIn().scale(),
              const SizedBox(height: 16),
              Container(
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                      colors: [AppTheme.accentBlue, AppTheme.accentCyan]),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: ElevatedButton.icon(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => Screen4SeverityDashboard(
                          analysisResult: widget.analysisResult),
                    ),
                  ),
                  icon: const Icon(Icons.arrow_forward,
                      color: Colors.white),
                  label: const Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('Next',
                          style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w600,
                              fontSize: 16)),
                      Text('اگلا',
                          style: TextStyle(
                              fontSize: 12, color: Colors.white70)),
                    ],
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    minimumSize: const Size(double.infinity, 0),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ).animate().fadeIn(delay: 300.ms),
            ],
          ],
        ),
      ),
    );
  }
}
