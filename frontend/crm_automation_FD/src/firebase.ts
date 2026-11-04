import { getAnalytics, isSupported } from 'firebase/analytics'
import { getApp, getApps, initializeApp, type FirebaseOptions } from 'firebase/app'

const firebaseConfig: FirebaseOptions = {
  apiKey: 'AIzaSyDZ-5aFmwmjHT83jyV3gnUojDexLq0eQ44',
  authDomain: 'real-estate-crm-automati-dbeaa.firebaseapp.com',
  projectId: 'real-estate-crm-automati-dbeaa',
  storageBucket: 'real-estate-crm-automati-dbeaa.firebasestorage.app',
  messagingSenderId: '254209105024',
  appId: '1:254209105024:web:02c94a3c740e610766da65',
  measurementId: 'G-GB88D6R1QG',
}

export const firebaseApp = getApps().length
  ? getApp()
  : initializeApp(firebaseConfig)

export const analyticsReady = isSupported()
  .then((supported) => (supported ? getAnalytics(firebaseApp) : null))
  .catch((error: unknown) => {
    console.warn('Firebase Analytics is unavailable in this browser.', error)
    return null
  })