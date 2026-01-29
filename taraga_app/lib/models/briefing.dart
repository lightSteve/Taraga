/// Data model for daily market briefing
class Briefing {
  final DateTime date;
  final String usSummary;
  final String? marketSentiment;
  final Map<String, dynamic>? keyIndices;

  Briefing({
    required this.date,
    required this.usSummary,
    this.marketSentiment,
    this.keyIndices,
  });

  factory Briefing.fromJson(Map<String, dynamic> json) {
    return Briefing(
      date: DateTime.parse(json['date'] as String),
      usSummary: json['us_summary'] as String,
      marketSentiment: json['market_sentiment'] as String?,
      keyIndices: json['key_indices_json'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date.toIso8601String(),
      'us_summary': usSummary,
      'market_sentiment': marketSentiment,
      'key_indices_json': keyIndices,
    };
  }
}
