import React, { useState } from 'react';
import { TouchableOpacity, View, Modal, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AccessibilityPanel from './AccessibilityPanel';
import { useAccessibility } from './AccessibilityContext';


export default function FloatingAccessibilityButton() {
const [open, setOpen] = useState(false);
const { state } = useAccessibility();


return (
<>
<TouchableOpacity
accessibilityLabel="Abrir configurações de acessibilidade"
activeOpacity={0.8}
onPress={() => setOpen(true)}
style={[styles.button, state.highContrast && styles.buttonHighContrast]}
>
<Ionicons name="accessibility" size={26} color="#fff" />
</TouchableOpacity>


<Modal visible={open} animationType="slide" onRequestClose={() => setOpen(false)} transparent>
<View style={styles.modalOverlay}>
<AccessibilityPanel onClose={() => setOpen(false)} />
</View>
</Modal>
</>
);
}


const styles = StyleSheet.create({
button: {
position: 'absolute',
right: 18,
bottom: 30,
width: 56,
height: 56,
borderRadius: 28,
backgroundColor: '#0A84FF',
justifyContent: 'center',
alignItems: 'center',
elevation: 6,
shadowColor: '#000',
shadowOpacity: 0.25,
shadowRadius: 6,
zIndex: 9999,
},
buttonHighContrast: {
backgroundColor: '#000',
},
modalOverlay: {
flex: 1,
backgroundColor: 'rgba(0,0,0,0.35)',
justifyContent: 'flex-end',
},
});