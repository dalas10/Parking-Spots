import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { ActivityIndicator, View } from 'react-native';

import { useAuthStore } from '../stores';

// Auth screens
import { LoginScreen, RegisterScreen } from '../screens/auth';

// Main screens
import { HomeScreen } from '../screens/home/HomeScreen';
import { ParkingSpotDetailScreen } from '../screens/parking/ParkingSpotDetailScreen';
import { BookingsScreen } from '../screens/bookings/BookingsScreen';
import { ProfileScreen } from '../screens/profile/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const AuthStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="Login" component={LoginScreen} />
    <Stack.Screen name="Register" component={RegisterScreen} />
  </Stack.Navigator>
);

const HomeStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="HomeMain"
      component={HomeScreen}
      options={{ headerShown: false }}
    />
    <Stack.Screen
      name="ParkingSpotDetail"
      component={ParkingSpotDetailScreen}
      options={{ title: 'Parking Spot' }}
    />
  </Stack.Navigator>
);

const BookingsStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="BookingsMain"
      component={BookingsScreen}
      options={{ title: 'My Bookings' }}
    />
  </Stack.Navigator>
);

const ProfileStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="ProfileMain"
      component={ProfileScreen}
      options={{ title: 'Profile' }}
    />
  </Stack.Navigator>
);

const MainTabs = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused }) => {
        let emoji = '';

        if (route.name === 'Home') {
          emoji = focused ? '🗺️' : '🗺️';
        } else if (route.name === 'Bookings') {
          emoji = focused ? '📅' : '📅';
        } else if (route.name === 'Profile') {
          emoji = focused ? '👤' : '👤';
        }

        return (
          <View style={{ opacity: focused ? 1 : 0.5 }}>
            <View style={{ fontSize: 24 }}>
              {/* Using Text for emoji in production */}
            </View>
          </View>
        );
      },
      tabBarActiveTintColor: '#4F46E5',
      tabBarInactiveTintColor: 'gray',
      headerShown: false,
    })}
  >
    <Tab.Screen
      name="Home"
      component={HomeStack}
      options={{ tabBarLabel: 'Explore' }}
    />
    <Tab.Screen
      name="Bookings"
      component={BookingsStack}
      options={{ tabBarLabel: 'Bookings' }}
    />
    <Tab.Screen
      name="Profile"
      component={ProfileStack}
      options={{ tabBarLabel: 'Profile' }}
    />
  </Tab.Navigator>
);

export const AppNavigator = () => {
  const { isAuthenticated, checkAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      await checkAuth();
      setIsLoading(false);
    };
    initAuth();
  }, []);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {isAuthenticated ? <MainTabs /> : <AuthStack />}
    </NavigationContainer>
  );
};
