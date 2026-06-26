module.exports = {
  preset: "jest-expo",
  testMatch: ["**/__tests__/**/*.test.js"],
  collectCoverageFrom: [
    "lib/aplicacao/**/*.js",
    "hooks/useAuth.js",
  ],
  moduleNameMapper: {
    "^@env$": "<rootDir>/__mocks__/@env.js",
  },
  transformIgnorePatterns: [
    "node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg)",
  ],
};
