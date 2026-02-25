import React, { useRef, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import {
  SafeAreaView,
  ActivityIndicator,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  BackHandler,
} from 'react-native';
import { WebView } from 'react-native-webview';

const SERVER_URL = 'http://192.168.53.100:3000';

export default function App() {
  const webviewRef = useRef<WebView>(null);
  const [canGoBack, setCanGoBack] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // Android back button navigates inside the WebView
  React.useEffect(() => {
    const onBack = () => {
      if (canGoBack && webviewRef.current) {
        webviewRef.current.goBack();
        return true;
      }
      return false;
    };
    const sub = BackHandler.addEventListener('hardwareBackPress', onBack);
    return () => sub.remove();
  }, [canGoBack]);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="auto" />

      {loading && !error && (
        <View style={styles.loader}>
          <ActivityIndicator size="large" color="#FDB82E" />
          <Text style={styles.loaderText}>Loading Urbee...</Text>
        </View>
      )}

      {error ? (
        <View style={styles.errorContainer}>
          <Text style={styles.errorEmoji}>⚠️</Text>
          <Text style={styles.errorTitle}>Can't reach the server</Text>
          <Text style={styles.errorMsg}>
            Make sure the server is running and your phone is on the same WiFi as{'\n'}
            <Text style={styles.errorUrl}>{SERVER_URL}</Text>
          </Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => {
              setError(false);
              setLoading(true);
              webviewRef.current?.reload();
            }}
          >
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <WebView
          ref={webviewRef}
          source={{ uri: SERVER_URL }}
          style={styles.webview}
          onLoadStart={() => { setLoading(true); setError(false); }}
          onLoadEnd={() => setLoading(false)}
          onError={() => { setLoading(false); setError(true); }}
          onHttpError={() => { setLoading(false); setError(true); }}
          onNavigationStateChange={(state) => setCanGoBack(state.canGoBack)}
          javaScriptEnabled
          domStorageEnabled
          geolocationEnabled
          allowsInlineMediaPlayback
          mediaPlaybackRequiresUserAction={false}
          mixedContentMode="always"
          userAgent="Mozilla/5.0 (Linux; Android 13) UrbeeApp/1.0"
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  webview: { flex: 1 },
  loader: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    zIndex: 10,
  },
  loaderText: { marginTop: 12, color: '#555', fontSize: 14 },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    backgroundColor: '#fff',
  },
  errorEmoji: { fontSize: 48, marginBottom: 16 },
  errorTitle: { fontSize: 20, fontWeight: '700', color: '#1a1a1a', marginBottom: 8 },
  errorMsg: { fontSize: 14, color: '#666', textAlign: 'center', lineHeight: 22 },
  errorUrl: { fontWeight: '700', color: '#FDB82E' },
  retryButton: {
    marginTop: 24,
    backgroundColor: '#FDB82E',
    paddingHorizontal: 32,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryText: { color: '#fff', fontWeight: '700', fontSize: 16 },
});
