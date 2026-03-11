import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

/// User service for device-based identification
/// Designed to support future subscription model
class UserService {
  static const String _userUuidKey = 'user_uuid';
  static const String _subscriptionStatusKey = 'subscription_status';
  static const String _subscriptionTierKey = 'subscription_tier';

  /// Get or create user UUID
  /// This UUID persists across app sessions and identifies the device
  Future<String> getUserUuid() async {
    final prefs = await SharedPreferences.getInstance();
    String? uuid = prefs.getString(_userUuidKey);

    if (uuid == null) {
      // Generate new UUID for first-time user
      uuid = const Uuid().v4();
      await prefs.setString(_userUuidKey, uuid);
    }

    return uuid;
  }

  /// Check if user has active subscription
  /// Returns true for premium users, false for free tier
  Future<bool> hasActiveSubscription() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_subscriptionStatusKey) ?? false;
  }

  /// Get subscription tier
  /// Returns: 'free', 'basic', 'premium'
  Future<String> getSubscriptionTier() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_subscriptionTierKey) ?? 'free';
  }

  /// Update subscription status (for future in-app purchase integration)
  Future<void> updateSubscription({
    required bool isActive,
    required String tier,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_subscriptionStatusKey, isActive);
    await prefs.setString(_subscriptionTierKey, tier);
  }

  /// Clear user data (for logout/reset)
  Future<void> clearUserData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_subscriptionStatusKey);
    await prefs.remove(_subscriptionTierKey);
    // Note: We keep user_uuid to maintain device identity
  }
}
