import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';
import 'screen5_response_plan.dart';

class Screen4SeverityDashboard extends StatelessWidget {
  final Map<String, dynamic> analysisResult;
  const Screen4SeverityDashboard({super.key, required this.analysisResult});

  @override
  Widget build(BuildContext context) {
    final a3 = analysisResult['a3_severity'] as Map<String, dynamic>;
    final a1 = analysisResult['a1_signals'] as Map<String, dynamic>;
    final double score = (a3['severity_score'] as num?)?.toDouble() ?? 3.0;
    final String auth = a3['authorization'] ?? 'REQUEST_VERIFICATION';
    final Map<String, dynamic> weights =
        Map<String, dynamic>.from(a3['weight_breakdown'] ?? {});
    final String? coordReasoning = a3['coordinator_reasoning'] as String?;
    final bool hasConflict = coordReasoning != null;
    final String location = a1['location_name'] ?? 'Unknown';

    final Color scoreColor = score >= 4
        ? AppTheme.alertCrimson
        : score >= 3
            ? AppTheme.warningAmber
            : AppTheme.successEmerald;

    // Severity text label
    final String severityLabel;
    final String severityLabelUrdu;
    final String severityEmoji;
    if (score >= 4) {
      severityEmoji = '🔴';
      severityLabel = 'Critical';
      severityLabelUrdu = 'نازک';
    } else if (score >= 3) {
      severityEmoji = '🟡';
      severityLabel = 'Serious';
      severityLabelUrdu = 'سنگین';
    } else {
      severityEmoji = '🟢';
      severityLabel = 'Moderate';
      severityLabelUrdu = 'معمولی';
    }

    final bool isDispatch = auth == 'DISPATCH_AUTHORIZED';

    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Assessment', style: TextStyle(fontSize: 18)),
            Text('جائزہ',
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
            // Subtitle – bilingual
            const Text(
              'Situation assessment',
              style: TextStyle(
                  color: AppTheme.textSecondary, fontStyle: FontStyle.italic),
            ),
            const Text(
              'صورتحال کا جائزہ',
              style: TextStyle(fontSize: 12, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 32),

            // Gauge
            Center(
              child: Column(
                children: [
                  Stack(
                    alignment: Alignment.center,
                    children: [
                      SizedBox(
                        width: 160,
                        height: 160,
                        child: TweenAnimationBuilder<double>(
                          tween: Tween<double>(begin: 0, end: score / 5.0),
                          duration: const Duration(milliseconds: 1800),
                          builder: (context, value, _) =>
                              CircularProgressIndicator(
                            value: value,
                            strokeWidth: 16,
                            backgroundColor: AppTheme.cardDark,
                            valueColor:
                                AlwaysStoppedAnimation<Color>(scoreColor),
                          ),
                        ),
                      ),
                      Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            score.toStringAsFixed(1),
                            style: Theme.of(context)
                                .textTheme
                                .displayLarge
                                ?.copyWith(fontSize: 52, color: scoreColor),
                          ),
                          const Text('/ 5.0',
                              style: TextStyle(
                                  fontSize: 16,
                                  color: AppTheme.textSecondary)),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // Severity text label – bilingual
                  Text(
                    '$severityEmoji $severityLabel',
                    style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: scoreColor),
                  ),
                  Text(
                    severityLabelUrdu,
                    style: TextStyle(fontSize: 14, color: scoreColor),
                  ),
                ],
              ),
            ).animate().fadeIn().scale(),

            const SizedBox(height: 28),

            // Weight breakdown – collapsed ExpansionTile
            if (weights.isNotEmpty)
              Card(
                child: ExpansionTile(
                  title: const Text('Technical Details',
                      style: TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: const Text('تکنیکی تفصیلات',
                      style: TextStyle(
                          fontSize: 12, color: AppTheme.textSecondary)),
                  initiallyExpanded: false,
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                      child: Column(
                        children: [
                          const Divider(),
                          ...weights.entries.map((e) => Padding(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 4),
                                child: Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: [
                                    Expanded(child: Text(e.key)),
                                    Text(
                                      e.value.toString(),
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: e.value
                                                .toString()
                                                .startsWith('-')
                                            ? AppTheme.alertCrimson
                                            : AppTheme.successEmerald,
                                      ),
                                    ),
                                  ],
                                ),
                              )),
                        ],
                      ),
                    ),
                  ],
                ),
              ).animate().fadeIn(delay: 400.ms),

            const SizedBox(height: 16),

            // Auth status – bilingual
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDispatch
                    ? AppTheme.successEmerald.withValues(alpha: 0.12)
                    : AppTheme.warningAmber.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isDispatch
                      ? AppTheme.successEmerald
                      : AppTheme.warningAmber,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    isDispatch
                        ? Icons.check_circle
                        : Icons.search,
                    color: isDispatch
                        ? AppTheme.successEmerald
                        : AppTheme.warningAmber,
                    size: 32,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isDispatch
                              ? '✅ Help is being sent!'
                              : '🔍 Verifying report',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: isDispatch
                                ? AppTheme.successEmerald
                                : AppTheme.warningAmber,
                            fontSize: 15,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          isDispatch
                              ? 'مدد بھیجی جا رہی ہے'
                              : 'رپورٹ کی تصدیق ہو رہی ہے',
                          style: TextStyle(
                            color: isDispatch
                                ? AppTheme.successEmerald
                                : AppTheme.warningAmber,
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          isDispatch
                              ? 'Response teams are on their way to $location'
                              : 'We are double-checking the details',
                          style: const TextStyle(
                              color: AppTheme.textPrimary, fontSize: 13),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          isDispatch
                              ? 'ردعمل ٹیمیں $location کی طرف جا رہی ہیں'
                              : 'تفصیلات دوبارہ جانچی جا رہی ہیں',
                          style: const TextStyle(
                              color: AppTheme.textSecondary,
                              fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ).animate().fadeIn(delay: 800.ms),

            // Coordinator reasoning – collapsed ExpansionTile
            if (hasConflict) ...[
              const SizedBox(height: 16),
              Card(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: const BorderSide(color: Colors.purple, width: 1),
                ),
                child: ExpansionTile(
                  leading:
                      const Icon(Icons.gavel, color: Colors.purple),
                  title: const Text('Details',
                      style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.purple)),
                  subtitle: const Text('تفصیلات',
                      style: TextStyle(
                          fontSize: 12, color: AppTheme.textSecondary)),
                  initiallyExpanded: false,
                  children: [
                    Padding(
                      padding:
                          const EdgeInsets.fromLTRB(16, 0, 16, 16),
                      child: Text(coordReasoning ?? '',
                          style:
                              const TextStyle(height: 1.5)),
                    ),
                  ],
                ),
              ).animate().fadeIn(delay: 1200.ms),
            ],

            const SizedBox(height: 28),

            // CTA button – bilingual
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: isDispatch
                      ? [
                          AppTheme.successEmerald,
                          const Color(0xFF059669)
                        ]
                      : [AppTheme.accentBlue, AppTheme.accentCyan],
                ),
                borderRadius: BorderRadius.circular(14),
              ),
              child: ElevatedButton.icon(
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) =>
                        Screen5ResponsePlan(analysisResult: analysisResult),
                  ),
                ),
                icon: Icon(
                  isDispatch ? Icons.groups : Icons.arrow_forward,
                  color: Colors.white,
                ),
                label: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      isDispatch ? 'See Help Teams' : 'Continue',
                      style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: 15),
                    ),
                    Text(
                      isDispatch ? 'مدد کی ٹیمیں دیکھیں' : 'جاری رکھیں',
                      style: const TextStyle(
                          fontSize: 12, color: Colors.white70),
                    ),
                  ],
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.transparent,
                  shadowColor: Colors.transparent,
                  padding: const EdgeInsets.symmetric(vertical: 18),
                  minimumSize: const Size(double.infinity, 0),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14)),
                ),
              ),
            ).animate().fadeIn(delay: 1600.ms),
          ],
        ),
      ),
    );
  }
}
