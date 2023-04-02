import * as base16384 from 'base16384';

// eslint-disable-next-line @typescript-eslint/no-namespace
export namespace QDVC {
  export const RE =
    /^qdvc:(?<device>(?:[a-zA-Z0-9+/=]|[\u3D00-\u3D08\u4E00-\u8DFF])+)(?:,(?<session>(?:[a-zA-Z0-9+/=]|[\u3D00-\u3D08\u4E00-\u8DFF])+))?$/;
  export type EncodingMethod = 'base64' | 'base16384';

  const isBase64 = (str: string) => /^[a-zA-Z0-9+/=]+$/.test(str);
  export const decodeBase64 = (encoded: string, text = false) =>
    text
      ? window.atob(encoded)
      : Uint8Array.from(window.atob(encoded), (c) => c.charCodeAt(0));
  export const encodeBase64 = (decoded: string | Uint8Array) =>
    window.btoa(
      decoded instanceof Uint8Array ? String.fromCharCode(...decoded) : decoded
    );

  const decodeBase16384 = (encoded: string, text = false) =>
    text
      ? new TextDecoder().decode(base16384.decode(encoded))
      : base16384.decode(encoded);
  const encodeBase16384 = (decoded: string | Uint8Array) =>
    String.fromCharCode(...base16384.encode(decoded));

  const adaptiveDecode = (encoded: string, text = false) =>
    isBase64(encoded)
      ? decodeBase64(encoded, text)
      : decodeBase16384(encoded, text);

  // eslint-disable-next-line vue/no-export-in-script-setup
  export function parse(uri: string) {
    const matched = RE.exec(uri);
    if (!matched) return null;
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const { device, session } = matched.groups!;
    return {
      device: adaptiveDecode(device, true) as string,
      session: session
        ? (adaptiveDecode(session, false) as Uint8Array)
        : undefined,
    };
  }

  // eslint-disable-next-line vue/no-export-in-script-setup
  export function stringify(
    data: { device: string; session?: string | Uint8Array },
    output: 'base64' | 'base16384'
  ) {
    const { device, session } = data;
    return output === 'base64'
      ? `qdvc:${encodeBase64(device)}${
          session ? `,${encodeBase64(session)}` : ''
        }`
      : `qdvc:${encodeBase16384(device)}${
          session ? `,${encodeBase16384(session)}` : ''
        }`;
  }
}
