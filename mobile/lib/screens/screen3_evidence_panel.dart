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
  int _visibleCount = 0;
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
    _evidenceItems = List<Map<String, dynamic>>.from(a2['evidence_checks'] ?? []);
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
    final color = {
      'SUPPORTS': AppTheme.successEmerald,
      'CONTRADICTS': AppTheme.alertCrimson,
      'NEUTRAL': AppTheme.textSecondary,
    }[verdict] ?? AppTheme.textSecondary;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(6)),
      child: Text(verdict, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
    );
  }

  IconData _sourceIcon(String source) {
    if (source.contains('Rain') || source.contains('Weather')) return Icons.water_drop;
    if (source.contains('Road')) return Icons.add_road;
    if (source.contains('Health')) return Icons.local_hospital;
    if (source.contains('Crop') || source.contains('Calendar')) return Icons.grass;
    if (source.contains('Missing') || source.contains('Nearby')) return Icons.campaign;
    return Icons.analytics;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Agent A2 — Evidence Verification')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Checking ${_evidenceItems.length} data sources...',
              style: TextStyle(color: AppTheme.textSecondary, fontStyle: FontStyle.italic),
            ),
            const SizedBox(height: 16),

            ...List.generate(_evidenceItems.length, (i) {
              if (i >= _visibleCount) return const SizedBox.shrink();
              final item = _evidenceItems[i];
              final verdict = item['verdict'] as String? ?? 'NEUTRAL';
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ExpansionTile(
                  leading: Icon(_sourceIcon(item['source'] ?? ''), color: AppTheme.accentCyan),
                  title: Text(item['source'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(item['value'] ?? ''),
                  trailing: _buildVerdictBadge(verdict),
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                      child: Text(
                        item['justification'] ?? '',
                        style: TextStyle(color: AppTheme.textSecondary, height: 1.4),
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn().slideX(begin: 0.05);
            }),

            if (_hasConflict) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppTheme.warningAmber.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppTheme.warningAmber),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.warning_amber_rounded, color: AppTheme.warningAmber),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Text(
                        'Conflict detected — Coordinator Agent X reviewing',
                        style: TextStyle(color: AppTheme.warningAmber, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn(),
            ],

            if (_showConfidence) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: _confidence == 'HIGH'
                        ? [AppTheme.successEmerald, const Color(0xFF059669)]
                        : _confidence == 'MEDIUM'
                            ? [AppTheme.warningAmber, const Color(0xFFD97706)]
                            : [AppTheme.alertCrimson, const Color(0xFFDC2626)],
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    const Text('Evidence Confidence', style: TextStyle(color: Colors.white70, fontSize: 13)),
                    const SizedBox(height: 4),
                    Text(_confidence, style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold)),
                  ],
                ),
              ).animate().fadeIn().scale(),
              const SizedBox(height: 16),
              Container(
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [AppTheme.accentBlue, AppTheme.accentCyan]),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: ElevatedButton(
                  onPressed: () => Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (_) => Screen4SeverityDashboard(analysisResult: widget.analysisResult),
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Continue to Severity Dashboard',
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                ),
              ).animate().fadeIn(delay: 300.ms),
            ],
          ],
        ),
      ),
    );
  }
}
