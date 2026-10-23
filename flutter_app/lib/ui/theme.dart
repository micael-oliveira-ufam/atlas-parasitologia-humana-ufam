import 'package:flutter/material.dart';

// Paleta: verde-azulado do atlas + cores de destaque por módulo + verde do brasão da UFAM.
const Color kTeal = Color(0xFF0F766E);
const Color kTealDark = Color(0xFF0B4F4A);
const Color kAmber = Color(0xFFD97706);
const Color kViolet = Color(0xFF7C3AED);
const Color kCoral = Color(0xFFE11D48);
const Color kSky = Color(0xFF0EA5E9);
const Color kUfamGreen = Color(0xFF00923F);

/// Cor de fundo do splash e de cabeçalhos (igual ao splash nativo do Android).
const Color kBrand = kTeal;

ThemeData buildTheme(Brightness brightness) {
  final dark = brightness == Brightness.dark;
  final scheme = ColorScheme.fromSeed(seedColor: kTeal, brightness: brightness);
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: dark ? const Color(0xFF0E1514) : const Color(0xFFF4F7F6),
    visualDensity: VisualDensity.standard,
    appBarTheme: AppBarTheme(
      centerTitle: false,
      elevation: 0,
      scrolledUnderElevation: 0,
      backgroundColor: dark ? const Color(0xFF0E1514) : const Color(0xFFF4F7F6),
      foregroundColor: scheme.onSurface,
      titleTextStyle: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: scheme.onSurface, letterSpacing: 0.2),
    ),
    navigationBarTheme: NavigationBarThemeData(
      height: 68,
      backgroundColor: dark ? const Color(0xFF16201F) : Colors.white,
      indicatorColor: kTeal.withAlpha(dark ? 90 : 40),
      labelTextStyle: WidgetStateProperty.resolveWith(
        (states) => TextStyle(
          fontSize: 12,
          fontWeight: states.contains(WidgetState.selected) ? FontWeight.w800 : FontWeight.w500,
        ),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
    ),
    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
  );
}

/// Cor de destaque de um módulo (campo "accent" do JSON).
Color accentFor(String accent) => switch (accent) {
      'amber' => kAmber,
      'violet' => kViolet,
      'coral' => kCoral,
      'sky' => kSky,
      _ => kTeal,
    };

/// Degradê do cabeçalho/cartão de um módulo.
LinearGradient gradientFor(String accent) {
  final c = accentFor(accent);
  final hsl = HSLColor.fromColor(c);
  final darker = hsl.withLightness((hsl.lightness - 0.16).clamp(0.0, 1.0)).toColor();
  final lighter = hsl.withLightness((hsl.lightness + 0.10).clamp(0.0, 1.0)).toColor();
  return LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [lighter, darker]);
}

/// Ícone de cada módulo (por id).
IconData iconForModule(String id) => switch (id) {
      'nematelmintos' => Icons.gesture,
      'platelmintos' => Icons.view_week_rounded,
      'protozoarios' => Icons.bubble_chart,
      _ => Icons.biotech,
    };

/// Superfície arredondada com borda suave (substitui o Card padrão nos blocos novos).
BoxDecoration softBox(BuildContext context, {Color? color, double radius = 18, Color? border}) {
  final dark = Theme.of(context).brightness == Brightness.dark;
  return BoxDecoration(
    color: color ?? (dark ? const Color(0xFF16201F) : Colors.white),
    borderRadius: BorderRadius.circular(radius),
    border: Border.all(color: border ?? (dark ? const Color(0xFF263634) : const Color(0xFFE2EAE8))),
  );
}

enum Tone { neutral, ok, warn, bad }

class ToneColors {
  const ToneColors(this.bg, this.fg);
  final Color bg;
  final Color fg;
}

/// Cores semânticas, com contraste para claro e escuro.
ToneColors toneColors(BuildContext context, Tone tone) {
  final dark = Theme.of(context).brightness == Brightness.dark;
  switch (tone) {
    case Tone.ok:
      return dark ? const ToneColors(Color(0xFF163021), Color(0xFF7FD69B)) : const ToneColors(Color(0xFFE0F5E7), Color(0xFF166534));
    case Tone.warn:
      return dark ? const ToneColors(Color(0xFF352A0C), Color(0xFFF0C15A)) : const ToneColors(Color(0xFFFEF3C7), Color(0xFF92400E));
    case Tone.bad:
      return dark ? const ToneColors(Color(0xFF3A1A1C), Color(0xFFFF9B9F)) : const ToneColors(Color(0xFFFFE4E6), Color(0xFF9F1239));
    case Tone.neutral:
      return dark ? const ToneColors(Color(0xFF1F2E2C), Color(0xFFB7D4CF)) : const ToneColors(Color(0xFFE6F2F0), Color(0xFF0B4F4A));
  }
}

/// Tom e rótulo do status de uma afirmação verificada.
Tone toneForClaim(String status) => switch (status) {
      'confirmado' => Tone.ok,
      'corrigido' => Tone.warn,
      'ressalva' => Tone.bad,
      _ => Tone.neutral,
    };
