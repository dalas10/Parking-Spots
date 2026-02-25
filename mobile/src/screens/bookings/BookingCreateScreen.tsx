import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { useBookingStore, useParkingSpotStore } from '../../stores';
import { Colors } from '../../constants/colors';

interface BookingCreateScreenProps {
  route: { params: { spotId: string } };
  navigation: any;
}

export const BookingCreateScreen: React.FC<BookingCreateScreenProps> = ({ route, navigation }) => {
  const { spotId } = route.params;

  const { selectedSpot, getSpotDetails } = useParkingSpotStore();
  const { createBooking, calculatePrice, calculatedPrice, isCalculatingPrice } = useBookingStore();

  // Default: start = now + 15 min, end = start + 1 hour
  const defaultStart = new Date(Date.now() + 15 * 60 * 1000);
  const defaultEnd = new Date(defaultStart.getTime() + 60 * 60 * 1000);

  const [startTime, setStartTime] = useState(defaultStart);
  const [endTime, setEndTime] = useState(defaultEnd);
  const [showStartPicker, setShowStartPicker] = useState(false);
  const [showEndPicker, setShowEndPicker] = useState(false);
  const [pickerMode, setPickerMode] = useState<'date' | 'time'>('date');
  const [activePicker, setActivePicker] = useState<'start' | 'end'>('start');

  const [vehiclePlate, setVehiclePlate] = useState('');
  const [vehicleMake, setVehicleMake] = useState('');
  const [vehicleModel, setVehicleModel] = useState('');
  const [vehicleColor, setVehicleColor] = useState('');
  const [specialRequests, setSpecialRequests] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const spot = selectedSpot?.id === spotId ? selectedSpot : null;

  useEffect(() => {
    if (!spot) {
      getSpotDetails(spotId);
    }
  }, [spotId]);

  // Recalculate price whenever times change
  useEffect(() => {
    if (startTime < endTime) {
      calculatePrice(spotId, startTime.toISOString(), endTime.toISOString()).catch(() => {});
    }
  }, [startTime, endTime]);

  const openPicker = (which: 'start' | 'end', mode: 'date' | 'time') => {
    setActivePicker(which);
    setPickerMode(mode);
    if (which === 'start') setShowStartPicker(true);
    else setShowEndPicker(true);
  };

  const handlePickerChange = (_: any, selected?: Date) => {
    setShowStartPicker(false);
    setShowEndPicker(false);
    if (!selected) return;

    if (activePicker === 'start') {
      const newStart = selected;
      setStartTime(newStart);
      // Push end forward if it's before new start
      if (newStart >= endTime) {
        setEndTime(new Date(newStart.getTime() + 60 * 60 * 1000));
      }
    } else {
      setEndTime(selected);
    }
  };

  const formatDateTime = (date: Date) =>
    date.toLocaleString('el-GR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

  const formatPrice = (cents: number) => `€${(cents / 100).toFixed(2)}`;

  const handleSubmit = async () => {
    setError(null);

    if (startTime < new Date()) {
      setError('Start time cannot be in the past.');
      return;
    }
    if (endTime <= startTime) {
      setError('End time must be after start time.');
      return;
    }
    if (!vehiclePlate.trim()) {
      setError('Please enter your vehicle plate number.');
      return;
    }

    setIsSubmitting(true);
    try {
      await createBooking({
        parking_spot_id: spotId,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        vehicle_plate: vehiclePlate.trim(),
        vehicle_make: vehicleMake.trim() || undefined,
        vehicle_model: vehicleModel.trim() || undefined,
        vehicle_color: vehicleColor.trim() || undefined,
        special_requests: specialRequests.trim() || undefined,
      });

      Alert.alert(
        'Booking Confirmed!',
        'Your parking spot has been booked successfully.',
        [{ text: 'OK', onPress: () => navigation.getParent()?.navigate('Bookings') }]
      );
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Booking failed. Please try again.';
      if (msg.includes('not available') || msg.includes('conflict') || msg.includes('overlapping')) {
        setError('This spot is already booked for the selected time. Please choose different times.');
      } else {
        setError(msg);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ScrollView style={styles.container} keyboardShouldPersistTaps="handled">
      {/* Header */}
      {spot && (
        <View style={styles.spotHeader}>
          <Text style={styles.spotName}>{spot.title}</Text>
          <Text style={styles.spotAddress}>{spot.address}, {spot.city}</Text>
        </View>
      )}

      {/* Error banner */}
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Date/Time */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Booking Times</Text>

        <Text style={styles.fieldLabel}>Start</Text>
        <View style={styles.dateRow}>
          <TouchableOpacity style={styles.datePart} onPress={() => openPicker('start', 'date')}>
            <Text style={styles.dateText}>{startTime.toLocaleDateString('el-GR')}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.datePart} onPress={() => openPicker('start', 'time')}>
            <Text style={styles.dateText}>
              {startTime.toLocaleTimeString('el-GR', { hour: '2-digit', minute: '2-digit' })}
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.fieldLabel}>End</Text>
        <View style={styles.dateRow}>
          <TouchableOpacity style={styles.datePart} onPress={() => openPicker('end', 'date')}>
            <Text style={styles.dateText}>{endTime.toLocaleDateString('el-GR')}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.datePart} onPress={() => openPicker('end', 'time')}>
            <Text style={styles.dateText}>
              {endTime.toLocaleTimeString('el-GR', { hour: '2-digit', minute: '2-digit' })}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {(showStartPicker || showEndPicker) && (
        <DateTimePicker
          value={activePicker === 'start' ? startTime : endTime}
          mode={pickerMode}
          is24Hour
          display={Platform.OS === 'ios' ? 'spinner' : 'default'}
          onChange={handlePickerChange}
          minimumDate={new Date()}
        />
      )}

      {/* Price summary */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Price Summary</Text>
        {isCalculatingPrice ? (
          <ActivityIndicator size="small" color={Colors.primary} />
        ) : calculatedPrice ? (
          <View style={styles.priceGrid}>
            <View style={styles.priceRow}>
              <Text style={styles.priceLabel}>Duration</Text>
              <Text style={styles.priceValue}>{calculatedPrice.duration_hours.toFixed(1)} hrs</Text>
            </View>
            <View style={styles.priceRow}>
              <Text style={styles.priceLabel}>Subtotal</Text>
              <Text style={styles.priceValue}>{formatPrice(calculatedPrice.subtotal)}</Text>
            </View>
            <View style={styles.priceRow}>
              <Text style={styles.priceLabel}>Service Fee</Text>
              <Text style={styles.priceValue}>{formatPrice(calculatedPrice.service_fee)}</Text>
            </View>
            <View style={[styles.priceRow, styles.priceTotal]}>
              <Text style={styles.priceTotalLabel}>Total</Text>
              <Text style={styles.priceTotalValue}>{formatPrice(calculatedPrice.total)}</Text>
            </View>
          </View>
        ) : (
          <Text style={styles.pricePlaceholder}>Select valid times to see price</Text>
        )}
      </View>

      {/* Vehicle info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Vehicle Info</Text>

        <Text style={styles.fieldLabel}>Plate Number *</Text>
        <TextInput
          style={styles.input}
          value={vehiclePlate}
          onChangeText={setVehiclePlate}
          placeholder="e.g. ZKY-1234"
          autoCapitalize="characters"
        />

        <Text style={styles.fieldLabel}>Make</Text>
        <TextInput
          style={styles.input}
          value={vehicleMake}
          onChangeText={setVehicleMake}
          placeholder="e.g. Toyota"
          autoCapitalize="words"
        />

        <Text style={styles.fieldLabel}>Model</Text>
        <TextInput
          style={styles.input}
          value={vehicleModel}
          onChangeText={setVehicleModel}
          placeholder="e.g. Corolla"
          autoCapitalize="words"
        />

        <Text style={styles.fieldLabel}>Color</Text>
        <TextInput
          style={styles.input}
          value={vehicleColor}
          onChangeText={setVehicleColor}
          placeholder="e.g. White"
          autoCapitalize="words"
        />
      </View>

      {/* Special requests */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Special Requests</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          value={specialRequests}
          onChangeText={setSpecialRequests}
          placeholder="Any special instructions..."
          multiline
          numberOfLines={3}
        />
      </View>

      {/* Submit */}
      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitButtonText}>
              Confirm Booking{calculatedPrice ? ` · ${formatPrice(calculatedPrice.total)}` : ''}
            </Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  spotHeader: { backgroundColor: '#fff', padding: 16, marginBottom: 8 },
  spotName: { fontSize: 18, fontWeight: '700', color: '#1a1a1a' },
  spotAddress: { fontSize: 13, color: '#666', marginTop: 2 },
  errorBanner: {
    margin: 12,
    padding: 12,
    backgroundColor: '#FEE2E2',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  errorText: { color: '#DC2626', fontSize: 14 },
  section: { backgroundColor: '#fff', margin: 8, borderRadius: 12, padding: 16 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#1a1a1a', marginBottom: 12 },
  fieldLabel: { fontSize: 13, fontWeight: '600', color: '#555', marginBottom: 4, marginTop: 8 },
  dateRow: { flexDirection: 'row', gap: 8 },
  datePart: {
    flex: 1,
    padding: 10,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center',
  },
  dateText: { fontSize: 14, color: '#1a1a1a' },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 10,
    fontSize: 14,
    backgroundColor: '#fafafa',
    marginBottom: 4,
  },
  textArea: { height: 80, textAlignVertical: 'top' },
  priceGrid: { gap: 6 },
  priceRow: { flexDirection: 'row', justifyContent: 'space-between' },
  priceLabel: { fontSize: 14, color: '#666' },
  priceValue: { fontSize: 14, color: '#1a1a1a' },
  priceTotal: {
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingTop: 8,
    marginTop: 4,
  },
  priceTotalLabel: { fontSize: 16, fontWeight: '700', color: '#1a1a1a' },
  priceTotalValue: { fontSize: 16, fontWeight: '700', color: Colors.primary },
  pricePlaceholder: { color: '#999', fontSize: 14 },
  footer: { padding: 16 },
  submitButton: {
    backgroundColor: Colors.primary,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  submitButtonDisabled: { opacity: 0.6 },
  submitButtonText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});
