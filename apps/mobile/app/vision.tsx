import React, { useState } from "react";
import { Button, Text, View } from "react-native";
import Tts from "react-native-tts";
import Voice from "@react-native-voice/voice";

export default function VisionMate() {
  const [text, setText] = useState("");

  const startListening = () => {
    Voice.start("en-US");
    Voice.onSpeechResults = async (e) => {
    const spoken = e.value?.[0] ?? "";
    if (!spoken) return;
      const res = await fetch("http://192.168.1.10:5001/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_query: spoken }),
      });
      const data = await res.json();
      setText(data.reply);
      Tts.speak(data.reply);
    };
  };

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Button title="Speak" onPress={startListening} />
      <Text>{text}</Text>
    </View>
  );
}
