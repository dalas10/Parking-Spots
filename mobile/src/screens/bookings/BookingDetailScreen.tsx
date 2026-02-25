import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { format } from 'date-fns';
import { useBookingStore } from '../../stores';
import { Colors } from '../../constants/colors';

interface BookingDetailScreenProps {
  route: { params: { bookingId: string } };
  navigation: any;
}

export const BookingDetailScreen: React.FC<BookingDetailScreenProps> = ({ route, navigation }) => {
  const { bookingId } = route.params;
  const { currentBooking, getBookingDetails, cancelBooking } = useBookingStore();

  useEffect(() => {
    getBookingDetails(bookingId);
  }, [bookingId]);

  const formatPrice = (cents: number) => `€${(cents / 100).toFixed(2)}`;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':   return '#F59E0B';
      case 'confirmed': return '#10B981';
      case 'in_progress': return '#3B82F6';
      case 'completed': return '#6B7280';
      case 'cancelled':
      case 'refunded':  return '#EF4444';
      default:          return '#6B7280';
    }
  };

  const handleCancel = () => {
    Alert.alert(
      'Cancel Booking',
      'Are you sure you want to cancel this booking?',
      [
        { text: 'No', style: 'cancel' },
        {
          text: 'Yes, Cancel',
          style: 'destructive',
          onPress: async () => {
            try {
              await cancelBooking(bookingId, 'Cancelled by user');
              navigation.goBack();
            } catch {
              Alert.alert('Error', 'Failed to cancel booking. Please try again.');
            }
          },
        },
      ]
    );
  };

  if (!currentBooking || currentBooking.id !== bookingId) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  const booking = currentBooking;
  const canCancel = ['pending', 'confirmed'].includes(booking.status);

  return (
    <ScrollView style={styles.container}>
      {/* Status */}
      <View style={styles.statusCard}>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(booking.status) + '20' }]}>
          <Text style={[styles.statusText, { color: getStatusColor(booking.status) }]}>
            {booking.status.replace('_', ' ').toUpperCase()}
          </Text>
        </View>
        <Text style={styles.bookingId}>Booking #{booking.id.slice(0, 8).toUpperCase()}</Text>
      </View>

      {/* Dates */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Booking Period</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Check-in</Text>
          <Text style={styles.infoValue}>
            {format(new Date(booking.start_time), 'EEE, MMM d yyyy · HH:mm')}
          </Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Check-out</Text>
          <Text style={styles.infoValue}>
            {format(new Date(booking.end_time), 'EEE, MMM d yyyy · HH:mm')}
          </Text>
        </View>
      </View>

      {/* Payment */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Payment</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Subtotal</Text>
          <Text style={styles.infoValue}>{formatPrice(booking.total_amount - booking.service_fee)}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Service Fee</Text>
          <Text style={styles.infoValue}>{formatPrice(booking.service_fee)}</Text>
        </View>
        <View style={[styles.infoRow, styles.totalRow]}>
          <Text style={styles.totalLabel}>Total</Text>
          <Text style={styles.totalValue}>{formatPrice(booking.total_amount)}</Text>
        </View>
      </View>

      {/* Vehicle */}
      {booking.vehicle_plate && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Vehicle</Text>
          {booking.vehicle_plate && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Plate</Text>
              <Text style={styles.infoValue}>{booking.vehicle_plate}</Text>
            </View>
          )}
          {(booking.vehicle_make || booking.vehicle_model) && (
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Vehicle</Text>
              <Text style={styles.infoValue}>
                {[booking.vehicle_make, booking.vehicle_model, booking.vehicle_color]
                  .filter(Boolean).join(' ')}
              </Text>
            </View>
          )}
        </View>
      )}

      {/* Special requests */}
      {booking.special_requests && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Special Requests</Text>
          <Text style={styles.notes}>{booking.special_requests}</Text>
        </View>
      )}

      {/* Cancellation */}
      {booking.cancellation_reason && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cancellation Reason</Text>
          <Text style={styles.notes}>{booking.cancellation_reason}</Text>
        </View>
      )}

      {/* Cancel button */}
      {canCancel && (
        <TouchableOpacity style={styles.cancelButton} onPress={handleCancel}>
          <Text style={styles.cancelButtonText}>Cancel Booking</Text>
        </TouchableOpacity>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  statusCard: {
    backgroundColor: '#fff',
    padding: 16,
    alignItems: 'center',
    margin: 8,
    borderRadius: 12,
  },
  statusBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginBottom: 8,
  },
  statusText: { fontWeight: '700', fontSize: 14 },
  bookingId: { color: '#999', fontSize: 12 },
  section: { backgroundColor: '#fff', margin: 8, borderRadius: 12, padding: 16 },
  sectionTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a1a', marginBottom: 10 },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoLabel: { fontSize: 14, color: '#666' },
  infoValue: { fontSize: 14, color: '#1a1a1a', fontWeight: '500', flex: 1, textAlign: 'right' },
  totalRow: { borderBottomWidth: 0, marginTop: 4 },
  totalLabel: { fontSize: 16, fontWeight: '700', color: '#1a1a1a' },
  totalValue: { fontSize: 16, fontWeight: '700', color: Colors.primary },
  notes: { fontSize: 14, color: '#555', lineHeight: 20 },
  cancelButton: {
    margin: 16,
    padding: 14,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#EF4444',
    alignItems: 'center',
  },
  cancelButtonText: { color: '#EF4444', fontWeight: '700', fontSize: 16 },
});
