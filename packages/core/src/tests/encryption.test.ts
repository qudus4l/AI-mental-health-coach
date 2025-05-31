import { describe, expect, it } from 'vitest';
import { encrypt, decrypt } from '../encryption';

describe('Encryption Utilities', () => {
  const testKey = '12345678901234567890123456789012'; // 32 characters
  const testIv = '1234567890123456'; // 16 characters
  const testData = 'This is a test string for encryption';

  it('should encrypt and decrypt data correctly', () => {
    const encrypted = encrypt(testData, testKey, testIv);
    expect(encrypted).toBeDefined();
    expect(encrypted).not.toBe(testData);

    const decrypted = decrypt(encrypted, testKey, testIv);
    expect(decrypted).toBe(testData);
  });

  it('should throw an error with missing data', () => {
    // @ts-expect-error Testing invalid parameters
    expect(() => encrypt(null, testKey, testIv)).toThrow();
    // @ts-expect-error Testing invalid parameters
    expect(() => encrypt(testData, null, testIv)).toThrow();
    // @ts-expect-error Testing invalid parameters
    expect(() => encrypt(testData, testKey, null)).toThrow();
  });

  it('should throw an error with incorrect key length', () => {
    const shortKey = '123456';
    expect(() => encrypt(testData, shortKey, testIv)).toThrow('Encryption key must be 32 characters long');
  });

  it('should throw an error with incorrect IV length', () => {
    const shortIv = '123456';
    expect(() => encrypt(testData, testKey, shortIv)).toThrow('Encryption IV must be 16 characters long');
  });

  it('should throw an error when decrypting with missing data', () => {
    const encrypted = encrypt(testData, testKey, testIv);
    // @ts-expect-error Testing invalid parameters
    expect(() => decrypt(null, testKey, testIv)).toThrow();
    // @ts-expect-error Testing invalid parameters
    expect(() => decrypt(encrypted, null, testIv)).toThrow();
    // @ts-expect-error Testing invalid parameters
    expect(() => decrypt(encrypted, testKey, null)).toThrow();
  });

  it('should throw an error when decrypting with incorrect key', () => {
    const encrypted = encrypt(testData, testKey, testIv);
    const wrongKey = '09876543210987654321098765432109';
    const decrypted = decrypt(encrypted, wrongKey, testIv);
    expect(decrypted).not.toBe(testData);
  });
}); 