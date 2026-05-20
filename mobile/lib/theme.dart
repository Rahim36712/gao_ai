import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ── Modern dark palette ──
  static const Color bgDark = Color(0xFF0F172A);
  static const Color surfaceDark = Color(0xFF1E293B);
  static const Color cardDark = Color(0xFF334155);
  static const Color accentBlue = Color(0xFF3B82F6);
  static const Color accentCyan = Color(0xFF06B6D4);
  static const Color alertCrimson = Color(0xFFEF4444);
  static const Color successEmerald = Color(0xFF10B981);
  static const Color warningAmber = Color(0xFFF59E0B);
  static const Color textPrimary = Color(0xFFF1F5F9);
  static const Color textSecondary = Color(0xFF94A3B8);

  // Legacy aliases so existing code still compiles
  static const Color primaryNavy = bgDark;
  static const Color bgWhite = bgDark;

  // ── Bilingual helpers ──
  /// Returns a Column with English label on top and Urdu label below (smaller, secondary color)
  static Widget bilingualLabel(String english, String urdu, {
    double englishSize = 16,
    double urduSize = 13,
    FontWeight englishWeight = FontWeight.w600,
    Color? englishColor,
    Color? urduColor,
    CrossAxisAlignment alignment = CrossAxisAlignment.start,
  }) {
    return Column(
      crossAxisAlignment: alignment,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          english,
          style: GoogleFonts.poppins(
            fontSize: englishSize,
            fontWeight: englishWeight,
            color: englishColor ?? textPrimary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          urdu,
          style: GoogleFonts.inter(
            fontSize: urduSize,
            color: urduColor ?? textSecondary,
          ),
          textDirection: TextDirection.rtl,
        ),
      ],
    );
  }

  /// Returns a single-line bilingual text "English / اردو"
  static Widget bilingualInline(String english, String urdu, {
    double fontSize = 16,
    FontWeight fontWeight = FontWeight.w600,
    Color? color,
  }) {
    return Text(
      '$english / $urdu',
      style: GoogleFonts.poppins(
        fontSize: fontSize,
        fontWeight: fontWeight,
        color: color ?? textPrimary,
      ),
    );
  }

  static ThemeData get lightTheme => darkTheme;

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      primaryColor: accentBlue,
      scaffoldBackgroundColor: bgDark,
      cardColor: surfaceDark,
      canvasColor: surfaceDark,
      // Ensure minimum touch target size of 48px for accessibility
      materialTapTargetSize: MaterialTapTargetSize.padded,
      visualDensity: VisualDensity.standard,
      appBarTheme: AppBarTheme(
        backgroundColor: surfaceDark,
        foregroundColor: textPrimary,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: GoogleFonts.poppins(
          fontWeight: FontWeight.w600,
          fontSize: 20,
          color: textPrimary,
        ),
      ),
      textTheme: TextTheme(
        displayLarge: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: textPrimary),
        displayMedium: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: textPrimary),
        titleLarge: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: textPrimary, fontSize: 22),
        titleMedium: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: textPrimary, fontSize: 18),
        bodyLarge: GoogleFonts.inter(fontSize: 16, color: textPrimary),
        bodyMedium: GoogleFonts.inter(fontSize: 15, color: textSecondary),
        bodySmall: GoogleFonts.inter(fontSize: 13, color: textSecondary),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: accentBlue,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 28),
          minimumSize: const Size(48, 48), // Accessible touch target
          elevation: 0,
          textStyle: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 16),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: accentCyan,
          minimumSize: const Size(48, 48),
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 24),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          side: BorderSide(color: accentCyan.withOpacity(0.5)),
          textStyle: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 15),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: cardDark,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: textSecondary.withOpacity(0.2)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: accentBlue, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: alertCrimson, width: 1.5),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: alertCrimson, width: 2),
        ),
        errorStyle: GoogleFonts.inter(color: alertCrimson, fontSize: 13),
        hintStyle: GoogleFonts.inter(color: textSecondary.withOpacity(0.5), fontSize: 15),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      ),
      cardTheme: CardThemeData(
        color: surfaceDark,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: textSecondary.withOpacity(0.1)),
        ),
        margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 0),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: cardDark,
        selectedColor: accentBlue.withOpacity(0.2),
        labelStyle: GoogleFonts.inter(fontSize: 14, color: textPrimary),
        secondaryLabelStyle: GoogleFonts.inter(fontSize: 14, color: accentBlue),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        side: BorderSide(color: textSecondary.withOpacity(0.15)),
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: surfaceDark,
        selectedItemColor: accentCyan,
        unselectedItemColor: textSecondary,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
        selectedLabelStyle: GoogleFonts.inter(fontWeight: FontWeight.w600, fontSize: 12),
        unselectedLabelStyle: GoogleFonts.inter(fontSize: 12),
      ),
      colorScheme: const ColorScheme.dark(
        primary: accentBlue,
        secondary: accentCyan,
        error: alertCrimson,
        surface: surfaceDark,
      ),
      dividerColor: textSecondary.withOpacity(0.12),
    );
  }
}

class DemoBannerWrapper extends StatelessWidget {
  final Widget child;
  const DemoBannerWrapper({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppTheme.alertCrimson.withOpacity(0.9),
                AppTheme.warningAmber.withOpacity(0.8),
              ],
            ),
          ),
          padding: const EdgeInsets.symmetric(vertical: 3),
          child: SafeArea(
            bottom: false,
            child: Text(
              '⚠  SYNTHETIC DEMO DATA — ALL DATA IS FICTIONAL  ⚠',
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.5,
              ),
            ),
          ),
        ),
        Expanded(child: child),
      ],
    );
  }
}
