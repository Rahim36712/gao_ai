import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme.dart';
import 'screen1_crisis_input.dart';
import 'screen7_missing_persons.dart';
import 'screen8_aid_distribution.dart';

class HomeScreen extends StatelessWidget {
  /// Callback to trigger demo mode from outside (triple-tap on logo)
  final VoidCallback? onDemoMode;

  const HomeScreen({super.key, this.onDemoMode});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 8),
          // ── Welcome Header ──
          Text(
            'Welcome / خوش آمدید',
            style: GoogleFonts.poppins(
              fontSize: 26,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'What do you need help with?\nآپ کو کس مدد کی ضرورت ہے؟',
            style: GoogleFonts.inter(
              fontSize: 15,
              color: AppTheme.textSecondary,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 28),

          // ── Action Card 1: Report Crisis ──
          _ActionCard(
            icon: Icons.warning_amber_rounded,
            iconColor: AppTheme.alertCrimson,
            gradientColors: [
              AppTheme.alertCrimson.withOpacity(0.15),
              AppTheme.warningAmber.withOpacity(0.08),
            ],
            borderColor: AppTheme.alertCrimson.withOpacity(0.3),
            titleEn: 'Report Crisis',
            titleUr: 'مسئلہ بتائیں',
            descriptionEn: 'Report flood, health emergency, or any disaster',
            descriptionUr: 'سیلاب، صحت کی ایمرجنسی، یا کوئی آفت بتائیں',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const Screen1CrisisInput()),
              );
            },
          ).animate().fadeIn(duration: 400.ms).slideY(begin: 0.15, end: 0, duration: 400.ms),

          const SizedBox(height: 16),

          // ── Action Card 2: Missing Person ──
          _ActionCard(
            icon: Icons.person_search_rounded,
            iconColor: AppTheme.warningAmber,
            gradientColors: [
              AppTheme.warningAmber.withOpacity(0.12),
              Colors.orange.withOpacity(0.06),
            ],
            borderColor: AppTheme.warningAmber.withOpacity(0.3),
            titleEn: 'Missing Person',
            titleUr: 'لاپتہ افراد',
            descriptionEn: 'Search for or report a missing person',
            descriptionUr: 'لاپتہ شخص تلاش کریں یا رپورٹ درج کریں',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const Screen7MissingPersons()),
              );
            },
          ).animate().fadeIn(duration: 400.ms, delay: 150.ms).slideY(begin: 0.15, end: 0, duration: 400.ms, delay: 150.ms),

          const SizedBox(height: 16),

          // ── Action Card 3: Aid Distribution ──
          _ActionCard(
            icon: Icons.inventory_2_rounded,
            iconColor: AppTheme.successEmerald,
            gradientColors: [
              AppTheme.successEmerald.withOpacity(0.12),
              AppTheme.accentCyan.withOpacity(0.06),
            ],
            borderColor: AppTheme.successEmerald.withOpacity(0.3),
            titleEn: 'Aid Distribution',
            titleUr: 'امداد کی تقسیم',
            descriptionEn: 'Log and verify aid packages',
            descriptionUr: 'امدادی پیکجز کی تصدیق اور اندراج',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const Screen8AidDistribution()),
              );
            },
          ).animate().fadeIn(duration: 400.ms, delay: 300.ms).slideY(begin: 0.15, end: 0, duration: 400.ms, delay: 300.ms),

          const SizedBox(height: 32),

          // ── Status footer ──
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.surfaceDark,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.textSecondary.withOpacity(0.1)),
            ),
            child: Row(
              children: [
                Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    color: AppTheme.successEmerald,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.successEmerald.withOpacity(0.4),
                        blurRadius: 6,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'System Active / سسٹم فعال ہے',
                        style: GoogleFonts.poppins(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: AppTheme.successEmerald,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '11 AI agents monitoring • 50 villages covered',
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(duration: 500.ms, delay: 500.ms),
        ],
      ),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final List<Color> gradientColors;
  final Color borderColor;
  final String titleEn;
  final String titleUr;
  final String descriptionEn;
  final String descriptionUr;
  final VoidCallback onTap;

  const _ActionCard({
    required this.icon,
    required this.iconColor,
    required this.gradientColors,
    required this.borderColor,
    required this.titleEn,
    required this.titleUr,
    required this.descriptionEn,
    required this.descriptionUr,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        splashColor: iconColor.withOpacity(0.1),
        highlightColor: iconColor.withOpacity(0.05),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: gradientColors,
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: borderColor),
          ),
          child: Row(
            children: [
              // Icon circle
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.15),
                  shape: BoxShape.circle,
                  border: Border.all(color: iconColor.withOpacity(0.3), width: 2),
                ),
                child: Icon(icon, color: iconColor, size: 32),
              ),
              const SizedBox(width: 20),
              // Text content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      titleEn,
                      style: GoogleFonts.poppins(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    Text(
                      titleUr,
                      style: GoogleFonts.inter(
                        fontSize: 16,
                        color: iconColor.withOpacity(0.9),
                        fontWeight: FontWeight.w500,
                      ),
                      textDirection: TextDirection.rtl,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      descriptionEn,
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        color: AppTheme.textSecondary,
                      ),
                    ),
                    Text(
                      descriptionUr,
                      style: GoogleFonts.inter(
                        fontSize: 12,
                        color: AppTheme.textSecondary.withOpacity(0.8),
                      ),
                      textDirection: TextDirection.rtl,
                    ),
                  ],
                ),
              ),
              // Arrow
              Icon(
                Icons.arrow_forward_ios_rounded,
                color: AppTheme.textSecondary.withOpacity(0.5),
                size: 20,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
