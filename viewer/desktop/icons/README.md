# Shared Physics Wiki icon

Approved design: the **first** generated lowercase italic black psi on white,
before the stronger-italic and balanced-redraw variants. `italic-psi-original.png`
is an exact copy of that selected generated image, preserved as the master.
Master SHA256: `0267a05e82429a8f06131bf834856c1219baace685eb4e27f8390743e19bb8de`.

This is an AI-generated bitmap, not the earlier Georgia Bold vector logo.
Do not substitute a later generated variant, redraw or shear the glyph.
The native packaging only scales it, clips white tile corners and adds standard
transparent app-icon padding. Header/favicon use compact PNG derivatives.

Rebuild on macOS from the vault root:

```sh
swift viewer/desktop/icons/generate.swift
iconutil -c icns viewer/desktop/icons/PhysicsWiki.iconset -o viewer/desktop/icons/PhysicsWiki.icns
```

The generated ICNS and ICO are source assets; Windows builds need no macOS
tools. `preview.png` is the native-icon visual reference. The intermediate
`.iconset` can be removed after ICNS conversion. Rebuild/prepare the frontend
after updating the public PNGs, re-sign the Mac app after copying its ICNS,
and republish the Windows executable to embed ICO changes. Merely placing an
ICO beside an unchanged executable does not replace its icon.
