# Physics LLM Wiki

Current vault release: **1.0.1**

This is an LLM wiki for physics. It currently supports Oxford's third-year physics courses, but its structural design makes it easy to extend to a wider range of subjects and contexts. It is designed to produce more visually presentable answers than frontier LLM chatbots while grounding those answers more closely in sources specified by the user. From raw source documents (such as pdf), the system creates both agent-accessible versions (such as tex and md) and their locators. When a question is asked, an AI agent can use those locators to retrieve relevant material efficiently and provide a transparent record of the sources used and the steps taken.

The wiki also contains carefully designed workflows for producing diagrams, identifying mistakes in handwritten work, controlling answer format, handling follow-up questions, and ensuring that important instructions and relevant source material are read when needed. These functions are not described in full here for brevity. The easiest way to get started is to download or clone this repository and begin using it with an AI agent.

To see examples of the question-and-answer documents produced by the wiki, read the [B3 Atomic Problems worked examples](questions_and_answers/problem_sets/B3_Atomic_Problems_Questions_and_Answers.md), together with the accompanying workflow logs and source extracts in the same folder.

## Supplying Lecture Notes

To use this wiki properly for physics problem solving, first download the relevant lecture-note PDFs for the course from sources you are entitled to access and provide them to the AI agent. The wiki itself does not provide these lecture notes for copyright reasons. The agent will place the PDFs in the locations expected by the vault and convert them into agent-accessible versions, such as TeX or Markdown. This source-ingestion step is required before using the vault to solve physics problems.

The best way to browse the wiki is to open it as a vault in Obsidian. For users who have never used Obsidian, I have also created a wiki viewer app that provides an Obsidian-style reading experience for the Markdown files.

The viewer source code is included under `viewer/`. Compiled applications are distributed separately through the repository's Releases page.

Original software and content in this repository are available for non-commercial use under the terms described in [`LICENSE.md`](LICENSE.md).

## Installing the Wiki Viewer

**If you already use Obsidian, you do not need to install the wiki viewer.**

### macOS

The macOS viewer supports Apple Silicon Macs running macOS 11 or later.

1. Download `Physics-Wiki-Viewer-macOS-arm64-v1.0.0.zip` from the repository's Releases page and extract it.
2. Drag **Physics Wiki.app** into your Applications folder, then double-click it. Because the app is not notarized by Apple, macOS may say that it cannot verify the developer. Apple notarization requires Apple Developer Program membership, which costs US$99 per year. The source code is available in `viewer/` for inspection. Click **Done**.
3. Open **System Settings → Privacy & Security**, scroll down, and click **Open Anyway** next to the message about Physics Wiki. Confirm with your password or Touch ID, then click **Open Anyway** once more. This approval is needed only on first launch.
4. Select the downloaded wiki folder—the folder containing `index.md` and `CLAUDE.md`. To select a different vault later, use **File → Switch Vault…** (`⌘O`).

### Windows (Preview)

The Windows viewer targets Windows 11 x64. It has not yet been tested on a Windows computer, and Windows 10 compatibility has not been confirmed.

1. Download `Physics-Wiki-Viewer-Windows-x64-v1.0.0-preview.1.zip` from the repository's Releases page and extract the entire archive. Do not run the application from inside the ZIP.
2. Optionally run `Test Windows.cmd` to check the bundled server and runtime, then open **Physics Wiki.exe**. Keep the executable, DLL files, and `resources` folder together.
3. If the app reports that Microsoft Edge WebView2 Runtime is missing, install it from [Microsoft's official WebView2 page](https://developer.microsoft.com/microsoft-edge/webview2/). Python and .NET are already included.
4. Select the downloaded wiki folder—the folder containing `index.md` and `CLAUDE.md`. To select a different vault later, use **File → Switch Vault** (`Ctrl+O`).

The Windows preview is unsigned, so Windows may display an unfamiliar-app warning.
