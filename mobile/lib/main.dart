import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:http/http.dart' as http;
import 'package:gaon_guard_mobile/screens/home_screen.dart';
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
  int _logoTapCount = 0;
  DateTime? _lastTapTime;

  /// Handle triple-tap on logo to show demo mode (hidden from regular users)
  void _handleLogoTap() {
    final now = DateTime.now();
    if (_lastTapTime != null && now.difference(_lastTapTime!).inMilliseconds > 800) {
      _logoTapCount = 0;
    }
    _lastTapTime = now;
    _logoTapCount++;

    if (_logoTapCount >= 3) {
      _logoTapCount = 0;
      _showDemoModeSheet();
    }
  }

  void _showDemoModeSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.surfaceDark,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (ctx) => const _DemoModeSheet(),
    );
  }

  void _showAdminDrawer() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.surfaceDark,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40, height: 4,
                  decoration: BoxDecoration(
                    color: AppTheme.textSecondary.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Admin Tools / ایڈمن ٹولز',
                style: GoogleFonts.poppins(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textPrimary,
                ),
              ),
              Text(
                'For operators and administrators only',
                style: GoogleFonts.inter(
                  fontSize: 13,
                  color: AppTheme.textSecondary,
                ),
              ),
              const SizedBox(height: 16),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppTheme.accentBlue.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.analytics, color: AppTheme.accentBlue),
                ),
                title: Text('Agent Traces', style: GoogleFonts.poppins(
                  fontWeight: FontWeight.w600, color: AppTheme.textPrimary,
                )),
                subtitle: Text('View AI reasoning logs', style: GoogleFonts.inter(
                  fontSize: 13, color: AppTheme.textSecondary,
                )),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16, color: AppTheme.textSecondary),
                onTap: () {
                  Navigator.pop(ctx);
                  Navigator.push(context, MaterialPageRoute(
                    builder: (_) => const Screen9AgentTraceViewer(),
                  ));
                },
              ),
              const SizedBox(height: 8),
              ListTile(
                leading: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: AppTheme.accentCyan.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.compare_arrows, color: AppTheme.accentCyan),
                ),
                title: Text('Before vs After', style: GoogleFonts.poppins(
                  fontWeight: FontWeight.w600, color: AppTheme.textPrimary,
                )),
                subtitle: Text('Impact comparison', style: GoogleFonts.inter(
                  fontSize: 13, color: AppTheme.textSecondary,
                )),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16, color: AppTheme.textSecondary),
                onTap: () {
                  Navigator.pop(ctx);
                  Navigator.push(context, MaterialPageRoute(
                    builder: (_) => const Screen10BeforeAfter(),
                  ));
                },
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            GestureDetector(
              onTap: _handleLogoTap,
              child: Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppTheme.accentBlue, AppTheme.accentCyan],
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.shield, color: Colors.white, size: 18),
              ),
            ),
            const SizedBox(width: 10),
            const Text('Gaon Guard AI'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_rounded, color: AppTheme.textSecondary),
            tooltip: 'Admin Tools',
            onPressed: _showAdminDrawer,
          ),
        ],
      ),
      body: DemoBannerWrapper(
        child: HomeScreen(
          onDemoMode: _showDemoModeSheet,
        ),
      ),
    );
  }
}

// ── Demo Mode Bottom Sheet (moved from screen1, hidden behind triple-tap) ──
class _DemoModeSheet extends StatelessWidget {
  const _DemoModeSheet();

  @override
  Widget build(BuildContext context) {
    final cases = [
      {
        'icon': Icons.thunderstorm,
        'color': AppTheme.accentBlue,
        'title': 'Flood vs No Rain Conflict',
        'desc': 'A2 evidence contradicts A1 — Coordinator X arbitrates',
        'case': 1,
      },
      {
        'icon': Icons.location_off,
        'color': AppTheme.warningAmber,
        'title': 'Missing Location',
        'desc': 'Complaint with no village name or GPS',
        'case': 2,
      },
      {
        'icon': Icons.credit_card,
        'color': AppTheme.alertCrimson,
        'title': 'Duplicate CNIC',
        'desc': 'Same CNIC registered twice in aid distribution',
        'case': 3,
      },
      {
        'icon': Icons.gps_off,
        'color': Colors.deepOrange,
        'title': 'Team Non-Movement',
        'desc': 'Team not moving after 30 min — escalation triggered',
        'case': 4,
      },
      {
        'icon': Icons.help_outline,
        'color': AppTheme.textSecondary,
        'title': 'Low Confidence Report',
        'desc': 'Vague input with ambiguous signals',
        'case': 5,
      },
      {
        'icon': Icons.person_search,
        'color': AppTheme.warningAmber,
        'title': 'Match Below Threshold',
        'desc': 'Missing person match at 52% — operator review needed',
        'case': 6,
      },
    ];

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40, height: 4,
                decoration: BoxDecoration(
                  color: AppTheme.textSecondary.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const Icon(Icons.science, color: AppTheme.accentCyan),
                const SizedBox(width: 8),
                Text('Demo Mode', style: GoogleFonts.poppins(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textPrimary,
                )),
              ],
            ),
            Text(
              'Trigger pre-staged edge cases for demonstration',
              style: GoogleFonts.inter(fontSize: 13, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 16),
            ...cases.map((c) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Card(
                child: ListTile(
                  leading: Icon(c['icon'] as IconData, color: c['color'] as Color),
                  title: Text(c['title'] as String, style: GoogleFonts.poppins(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                    color: AppTheme.textPrimary,
                  )),
                  subtitle: Text(c['desc'] as String, style: GoogleFonts.inter(
                    fontSize: 12,
                    color: AppTheme.textSecondary,
                  )),
                  trailing: IconButton(
                    icon: const Icon(Icons.play_circle_fill, color: AppTheme.accentCyan),
                    onPressed: () => _triggerEdgeCase(context, c['case'] as int, c['title'] as String),
                  ),
                ),
              ),
            )),
          ],
        ),
      ),
    );
  }

  Future<void> _triggerEdgeCase(BuildContext context, int caseNum, String title) async {
    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        backgroundColor: AppTheme.surfaceDark,
        content: Row(
          children: [
            const CircularProgressIndicator(color: AppTheme.accentCyan),
            const SizedBox(width: 16),
            Expanded(child: Text('Running: $title...', style: GoogleFonts.inter(
              color: AppTheme.textPrimary,
            ))),
          ],
        ),
      ),
    );

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/demo/edge_case/$caseNum'),
      ).timeout(const Duration(seconds: 5));

      if (context.mounted) Navigator.pop(context); // close dialog

      if (response.statusCode == 200 && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('✅ $title — triggered successfully'),
          backgroundColor: AppTheme.successEmerald,
        ));
      }
    } catch (e) {
      if (context.mounted) Navigator.pop(context); // close dialog
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('❌ Failed: $e'),
          backgroundColor: AppTheme.alertCrimson,
        ));
      }
    }
  }
}
