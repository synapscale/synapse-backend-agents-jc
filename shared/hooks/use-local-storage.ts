import React from "react";

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = React.useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value: React.SetStateAction<T>) => {
    try {
      setStoredValue((prev) => {
        const valueToStore =
          typeof value === "function" ? (value as (val: T) => T)(prev) : value;
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
        return valueToStore;
      });
    } catch (error) {}
  };

  return [storedValue, setValue] as const;
}
