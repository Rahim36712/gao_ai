import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primaryNavy = Color(0xFF1A3A6B);
  static const Color accentBlue = Color(0xFF2563EB);
  static const Color alertCrimson = Color(0xFFDC2626);
  static const Color successEmerald = Color(0xFF059669);
  static const Color bgWhite = Color(0xFFFFFFFF);

  static ThemeData get lightTheme {
    return ThemeData(
      primaryColor: primaryNavy,
      scaffoldBackgroundColor: bgWhite,
      appBarTheme: AppBarTheme(
        backgroundColor: primaryNavy,
        foregroundColor: bgWhite,
        elevation: 0,
        titleTextStyle: GoogleFonts.poppins(
          fontWeight: FontWeight.w600,
          fontSize: 20,
          color: bgWhite,
        ),
      ),
      textTheme: TextTheme(
        displayLarge: GoogleFonts.poppins(fontWeight: FontWeight.bold, color: primaryNavy),
        displayMedium: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: primaryNavy),
        titleLarge: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: primaryNavy, fontSize: 22),
        titleMedium: GoogleFonts.poppins(fontWeight: FontWeight.w600, color: Colors.black87, fontSize: 18),
        bodyLarge: GoogleFonts.roboto(fontSize: 16, color: Colors.black87),
        bodyMedium: GoogleFonts.roboto(fontSize: 14, color: Colors.black87),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryNavy,
          foregroundColor: bgWhite,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          textStyle: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 16),
        ),
      ),
      colorScheme: const ColorScheme.light(
        primary: primaryNavy,
        secondary: accentBlue,
        error: alertCrimson,
        background: bgWhite,
      ),
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
          color: AppTheme.alertCrimson,
          padding: const EdgeInsets.symmetric(vertical: 2),
          child: SafeArea(
            bottom: false,
            child: Text(
              'SYNTHETIC DEMO DATA',
              textAlign: TextAlign.center,
              style: GoogleFonts.roboto(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
              ),
            ),
          ),
        ),
        Expanded(child: child),
      ],
    );
  }
}
