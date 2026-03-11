import 'package:flutter/material.dart';
import '../models/value_chain.dart';
import '../theme/app_theme.dart';

class ValueChainCard extends StatelessWidget {
  final ValueChainResponse valueChain;

  const ValueChainCard({super.key, required this.valueChain});

  @override
  Widget build(BuildContext context) {
    return NeonGlassCard(
      glowColor: AppColors.accentPurple, // Using a distinct color for this section
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: Theme Name
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.bgSecondary,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.hub_rounded,
                  color: AppColors.accentPurple,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      valueChain.theme,
                      style: TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      "Global Supply Chain Dependency",
                      style: TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // US Drivers List
          if (valueChain.usDrivers.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  "No data available for this theme.",
                  style: TextStyle(color: AppColors.textMuted),
                ),
              ),
            )
          else
            ...valueChain.usDrivers.entries.map((entry) {
              final usDriverName = entry.key;
              final krConnections = entry.value;

              return Padding(
                padding: const EdgeInsets.only(bottom: 24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // US Driver Item
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: AppColors.bgBlueLight.withOpacity(0.5),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                            color: AppColors.primary.withOpacity(0.3)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text("🇺🇸", style: TextStyle(fontSize: 16)),
                          const SizedBox(width: 8),
                          Text(
                            usDriverName,
                            style: TextStyle(
                              color: AppColors.textPrimary,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Connection Line (Vertical)
                    Container(
                      margin: const EdgeInsets.only(left: 20),
                      height: 16,
                      width: 2,
                      color: AppColors.border,
                    ),

                    // KR Connections
                    ...krConnections.map((item) => _buildConnectionItem(item)),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }

  Widget _buildConnectionItem(ValueChainItem item) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Connection Line (Branch)
          Container(
            margin: const EdgeInsets.only(left: 20, top: 12),
            width: 16,
            height: 2,
            color: AppColors.border,
          ),
          const SizedBox(width: 8),

          // KR Stock Card
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.bgSecondary.withOpacity(0.5),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.border.withOpacity(0.5)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Text("🇰🇷", style: TextStyle(fontSize: 14)),
                      const SizedBox(width: 8),
                      Text(
                        item.krStock, // This might be a ticker if name is missing, handle in logic or UI
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                      ),
                      const Spacer(),
                      if (item.relation.isNotEmpty)
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.accentPurple.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            item.relation,
                            style: const TextStyle(
                              color: AppColors.accentPurple,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                    ],
                  ),
                  if (item.description.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      item.description,
                      style: TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 12,
                        height: 1.4,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
