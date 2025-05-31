/**
 * Encryption utilities for sensitive data
 */
import CryptoJS from 'crypto-js';

/**
 * Encrypts sensitive data using AES-256-GCM
 * 
 * @param data - The data to encrypt
 * @param key - The encryption key (must be 32 bytes for AES-256)
 * @param iv - The initialization vector (must be 16 bytes)
 * @returns The encrypted data as a string
 */
export function encrypt(data: string, key: string, iv: string): string {
  if (!data || !key || !iv) {
    throw new Error('Data, key, and IV are required for encryption');
  }

  if (key.length !== 32) {
    throw new Error('Encryption key must be 32 characters long');
  }

  if (iv.length !== 16) {
    throw new Error('Encryption IV must be 16 characters long');
  }

  const keyBytes = CryptoJS.enc.Utf8.parse(key);
  const ivBytes = CryptoJS.enc.Utf8.parse(iv);
  
  const encrypted = CryptoJS.AES.encrypt(data, keyBytes, {
    iv: ivBytes,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  });
  
  return encrypted.toString();
}

/**
 * Decrypts sensitive data using AES-256-GCM
 * 
 * @param encryptedData - The data to decrypt
 * @param key - The encryption key (must be 32 bytes for AES-256)
 * @param iv - The initialization vector (must be 16 bytes)
 * @returns The decrypted data
 */
export function decrypt(encryptedData: string, key: string, iv: string): string {
  if (!encryptedData || !key || !iv) {
    throw new Error('Encrypted data, key, and IV are required for decryption');
  }

  if (key.length !== 32) {
    throw new Error('Encryption key must be 32 characters long');
  }

  if (iv.length !== 16) {
    throw new Error('Encryption IV must be 16 characters long');
  }

  const keyBytes = CryptoJS.enc.Utf8.parse(key);
  const ivBytes = CryptoJS.enc.Utf8.parse(iv);
  
  const decrypted = CryptoJS.AES.decrypt(encryptedData, keyBytes, {
    iv: ivBytes,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  });
  
  return decrypted.toString(CryptoJS.enc.Utf8);
} 