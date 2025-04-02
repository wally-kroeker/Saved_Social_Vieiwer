================================================
File: README.md
================================================
# npx offmute 🎙️

<div align="center">

[![NPM version](https://img.shields.io/npm/v/offmute.svg)](https://www.npmjs.com/package/offmute)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

**Intelligent meeting transcription and analysis using Google's Gemini models**

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Usage](#-usage) • [Advanced](#-advanced-usage) • [How It Works](#-how-it-works)

</div>

## 🚀 Features

- 🎯 **Transcription & Diarization**: Convert audio/video content to text while identifying different speakers
- 🎭 **Smart Speaker Identification**: Attempts to identify speakers by name and role when possible
- 📊 **Meeting Reports**: Generates structured reports with key points, action items, and participant profiles
- 🎬 **Video Analysis**: Extracts and analyzes visual information from video meetings, understand when demos are beign didsplayed
- ⚡ **Multiple Processing Tiers**: From budget-friendly to premium processing options
- 🔄 **Robust Processing**: Handles long meetings with automatic chunking and proper cleanup
- 📁 **Flexible Output**: Markdown-formatted transcripts and reports with optional intermediate outputs

## 🏃 Quick Start

```bash
# Set your Gemini API key
export GEMINI_API_KEY=your_key_here

# Run on a meeting recording
npx offmute path/to/your/meeting.mp4
```

## 📦 Installation

### As a CLI Tool

```bash
npx offmute <Meeting_Location> <options>
```

### As a Package

```bash
npm install offmute
```

## Get Help

```
npx offmute --help
```

`bunx` or `bun` works faster if you have it!

## 💻 Usage

### Command Line Interface

```bash
npx offmute <input-file> [options]
```

Options:

- `-t, --tier <tier>`: Processing tier (first, business, economy, budget) [default: "business"]
- `-a, --all`: Save all intermediate outputs
- `-sc, --screenshot-count <number>`: Number of screenshots to extract [default: 4]
- `-ac, --audio-chunk-minutes <number>`: Length of audio chunks in minutes [default: 10]
- `-r, --report`: Generate a structured meeting report
- `-rd, --reports-dir <path>`: Custom directory for report output

### Processing Tiers

- **First Tier** (`first`): Uses Gemini 2.0 Pro models for all operations
- **Business Tier** (`business`): Gemini 2.0 Pro for description and report, Gemini 2.0 Flash for transcription
- **Economy Tier** (`economy`): Gemini 2.0 Flash models for all operations
- **Budget Tier** (`budget`): Gemini 2.0 Flash for description, Gemini 2.0 Flash Lite for transcription and report

### As a Module

```typescript
import {
  generateDescription,
  generateTranscription,
  generateReport,
} from "offmute";

// Generate description and transcription
const description = await generateDescription(inputFile, {
  screenshotModel: "gemini-2.0-pro-exp-02-05",
  audioModel: "gemini-2.0-pro-exp-02-05",
  mergeModel: "gemini-2.0-pro-exp-02-05",
  showProgress: true,
});

const transcription = await generateTranscription(inputFile, description, {
  transcriptionModel: "gemini-2.0-pro-exp-02-05",
  showProgress: true,
});

// Generate a structured report
const report = await generateReport(
  description.finalDescription,
  transcription.chunkTranscriptions.join("\n\n"),
  {
    model: "gemini-2.0-pro-exp-02-05",
    reportName: "meeting_summary",
    showProgress: true,
  }
);
```

## 🔧 Advanced Usage

### Intermediate Outputs

When run with the `-a` flag, offmute saves intermediate processing files:

```
input_file_intermediates/
├── screenshots/          # Video screenshots
├── audio/               # Processed audio chunks
├── transcription/       # Per-chunk transcriptions
└── report/             # Report generation data
```

### Custom Chunk Sizes

Adjust processing for different content types:

```bash
# Longer chunks for presentations
offmute presentation.mp4 -ac 20

# More screenshots for visual-heavy content
offmute workshop.mp4 -sc 8
```

## ⚙️ How It Works

offmute uses a multi-stage pipeline:

1. **Content Analysis**

   - Extracts screenshots from videos at key moments
   - Chunks audio into processable segments
   - Generates initial descriptions of visual and audio content

2. **Transcription & Diarization**

   - Processes audio chunks with context awareness
   - Identifies and labels speakers
   - Maintains conversation flow across chunks

3. **Report Generation (Spreadfill)**
   - Uses a unique "Spreadfill" technique:
     1. Generates report structure with section headings
     2. Fills each section independently using full context
     3. Ensures coherent narrative while maintaining detailed coverage

### Spreadfill Technique

The Spreadfill approach helps maintain consistency while allowing detailed analysis:

```typescript
// 1. Generate structure
const structure = await generateHeadings(description, transcript);

// 2. Fill sections independently
const sections = await Promise.all(
  structure.sections.map((section) => generateSection(section, fullContext))
);

// 3. Combine into coherent report
const report = combineResults(sections);
```

## 🛠️ Requirements

- Node.js 14 or later
- ffmpeg installed on your system
- Google Gemini API key

## Contributing

You can start in `TODOs.md` to help with things I'm thinking about, or you can steel yourself and check out `PROBLEMS.md`.

Created by [Hrishi Olickel](https://twitter.com/hrishioa) • Support offmute by starring our [GitHub repository](https://github.com/southbridgeai/offmute)


================================================
File: LICENSE
================================================
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1.  Definitions.

    "License" shall mean the terms and conditions for use, reproduction,
    and distribution as defined by Sections 1 through 9 of this document.

    "Licensor" shall mean the copyright owner or entity authorized by
    the copyright owner that is granting the License.

    "Legal Entity" shall mean the union of the acting entity and all
    other entities that control, are controlled by, or are under common
    control with that entity. For the purposes of this definition,
    "control" means (i) the power, direct or indirect, to cause the
    direction or management of such entity, whether by contract or
    otherwise, or (ii) ownership of fifty percent (50%) or more of the
    outstanding shares, or (iii) beneficial ownership of such entity.

    "You" (or "Your") shall mean an individual or Legal Entity
    exercising permissions granted by this License.

    "Source" form shall mean the preferred form for making modifications,
    including but not limited to software source code, documentation
    source, and configuration files.

    "Object" form shall mean any form resulting from mechanical
    transformation or translation of a Source form, including but
    not limited to compiled object code, generated documentation,
    and conversions to other media types.

    "Work" shall mean the work of authorship, whether in Source or
    Object form, made available under the License, as indicated by a
    copyright notice that is included in or attached to the work
    (an example is provided in the Appendix below).

    "Derivative Works" shall mean any work, whether in Source or Object
    form, that is based on (or derived from) the Work and for which the
    editorial revisions, annotations, elaborations, or other modifications
    represent, as a whole, an original work of authorship. For the purposes
    of this License, Derivative Works shall not include works that remain
    separable from, or merely link (or bind by name) to the interfaces of,
    the Work and Derivative Works thereof.

    "Contribution" shall mean any work of authorship, including
    the original version of the Work and any modifications or additions
    to that Work or Derivative Works thereof, that is intentionally
    submitted to Licensor for inclusion in the Work by the copyright owner
    or by an individual or Legal Entity authorized to submit on behalf of
    the copyright owner. For the purposes of this definition, "submitted"
    means any form of electronic, verbal, or written communication sent
    to the Licensor or its representatives, including but not limited to
    communication on electronic mailing lists, source code control systems,
    and issue tracking systems that are managed by, or on behalf of, the
    Licensor for the purpose of discussing and improving the Work, but
    excluding communication that is conspicuously marked or otherwise
    designated in writing by the copyright owner as "Not a Contribution."

    "Contributor" shall mean Licensor and any individual or Legal Entity
    on behalf of whom a Contribution has been received by Licensor and
    subsequently incorporated within the Work.

2.  Grant of Copyright License. Subject to the terms and conditions of
    this License, each Contributor hereby grants to You a perpetual,
    worldwide, non-exclusive, no-charge, royalty-free, irrevocable
    copyright license to reproduce, prepare Derivative Works of,
    publicly display, publicly perform, sublicense, and distribute the
    Work and such Derivative Works in Source or Object form.

3.  Grant of Patent License. Subject to the terms and conditions of
    this License, each Contributor hereby grants to You a perpetual,
    worldwide, non-exclusive, no-charge, royalty-free, irrevocable
    (except as stated in this section) patent license to make, have made,
    use, offer to sell, sell, import, and otherwise transfer the Work,
    where such license applies only to those patent claims licensable
    by such Contributor that are necessarily infringed by their
    Contribution(s) alone or by combination of their Contribution(s)
    with the Work to which such Contribution(s) was submitted. If You
    institute patent litigation against any entity (including a
    cross-claim or counterclaim in a lawsuit) alleging that the Work
    or a Contribution incorporated within the Work constitutes direct
    or contributory patent infringement, then any patent licenses
    granted to You under this License for that Work shall terminate
    as of the date such litigation is filed.

4.  Redistribution. You may reproduce and distribute copies of the
    Work or Derivative Works thereof in any medium, with or without
    modifications, and in Source or Object form, provided that You
    meet the following conditions:

    (a) You must give any other recipients of the Work or
    Derivative Works a copy of this License; and

    (b) You must cause any modified files to carry prominent notices
    stating that You changed the files; and

    (c) You must retain, in the Source form of any Derivative Works
    that You distribute, all copyright, patent, trademark, and
    attribution notices from the Source form of the Work,
    excluding those notices that do not pertain to any part of
    the Derivative Works; and

    (d) If the Work includes a "NOTICE" text file as part of its
    distribution, then any Derivative Works that You distribute must
    include a readable copy of the attribution notices contained
    within such NOTICE file, excluding those notices that do not
    pertain to any part of the Derivative Works, in at least one
    of the following places: within a NOTICE text file distributed
    as part of the Derivative Works; within the Source form or
    documentation, if provided along with the Derivative Works; or,
    within a display generated by the Derivative Works, if and
    wherever such third-party notices normally appear. The contents
    of the NOTICE file are for informational purposes only and
    do not modify the License. You may add Your own attribution
    notices within Derivative Works that You distribute, alongside
    or as an addendum to the NOTICE text from the Work, provided
    that such additional attribution notices cannot be construed
    as modifying the License.

    You may add Your own copyright statement to Your modifications and
    may provide additional or different license terms and conditions
    for use, reproduction, or distribution of Your modifications, or
    for any such Derivative Works as a whole, provided Your use,
    reproduction, and distribution of the Work otherwise complies with
    the conditions stated in this License.

5.  Submission of Contributions. Unless You explicitly state otherwise,
    any Contribution intentionally submitted for inclusion in the Work
    by You to the Licensor shall be under the terms and conditions of
    this License, without any additional terms or conditions.
    Notwithstanding the above, nothing herein shall supersede or modify
    the terms of any separate license agreement you may have executed
    with Licensor regarding such Contributions.

6.  Trademarks. This License does not grant permission to use the trade
    names, trademarks, service marks, or product names of the Licensor,
    except as required for reasonable and customary use in describing the
    origin of the Work and reproducing the content of the NOTICE file.

7.  Disclaimer of Warranty. Unless required by applicable law or
    agreed to in writing, Licensor provides the Work (and each
    Contributor provides its Contributions) on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
    implied, including, without limitation, any warranties or conditions
    of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
    PARTICULAR PURPOSE. You are solely responsible for determining the
    appropriateness of using or redistributing the Work and assume any
    risks associated with Your exercise of permissions under this License.

8.  Limitation of Liability. In no event and under no legal theory,
    whether in tort (including negligence), contract, or otherwise,
    unless required by applicable law (such as deliberate and grossly
    negligent acts) or agreed to in writing, shall any Contributor be
    liable to You for damages, including any direct, indirect, special,
    incidental, or consequential damages of any character arising as a
    result of this License or out of the use or inability to use the
    Work (including but not limited to damages for loss of goodwill,
    work stoppage, computer failure or malfunction, or any and all
    other commercial damages or losses), even if such Contributor
    has been advised of the possibility of such damages.

9.  Accepting Warranty or Additional Liability. While redistributing
    the Work or Derivative Works thereof, You may choose to offer,
    and charge a fee for, acceptance of support, warranty, indemnity,
    or other liability obligations and/or rights consistent with this
    License. However, in accepting such obligations, You may act only
    on Your own behalf and on Your sole responsibility, not on behalf
    of any other Contributor, and only if You agree to indemnify,
    defend, and hold each Contributor harmless for any liability
    incurred by, or claims asserted against, such Contributor by reason
    of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


================================================
File: PROBLEMS.md
================================================
Here's Claude tearing this repo apart:

# Code Review: Transcription System

## Critical Issues

### 1. Error Handling and Recovery

- No proper handling of corrupt audio/video files in `processAudioFile`
- Missing checks for FFmpeg installation/availability
- No validation of audio/video file integrity before processing
- Limited retry logic for FFmpeg operations
- No disk space checks before starting large file operations

### 2. Resource Management

- No cleanup of temporary files in error scenarios in `processAudioFile`
- Memory usage not monitored during large file processing
- No limits on concurrent FFmpeg processes
- Missing cleanup of screenshots in error scenarios
- No timeout handling for hanging FFmpeg processes

### 3. Input Validation

- Missing validation for negative numbers in time-based parameters
- No maximum file size checks
- Limited MIME type validation
- No validation of aspect ratio for screenshots

## Functional Improvements

### 1. Performance

- Could implement parallel processing for screenshot extraction
- Audio chunking could be optimized with streaming
- Potential for WebAssembly FFmpeg to reduce process spawning
- Consider caching for repeated operations on same file
- Missing progress tracking for file uploads to Gemini

### 2. Accuracy

- No confidence scores for transcription results
- Missing speaker diarization validation
- No handling of background noise/music
- No quality checks on extracted screenshots
- No validation of transcription coherence between chunks

### 3. Usability

```typescript
interface GenerateDescriptionOptions {
  screenshotModel: string;
  screenshotCount?: number;
  audioModel: string;
  descriptionChunkMinutes?: number;
  transcriptionChunkMinutes?: number;
  mergeModel: string;
  outputPath?: string;
  showProgress?: boolean;
}
```

Could be improved with:

- Model validation
- Default values documentation
- Configuration validation
- Type safety for model names
- Clear documentation of units (minutes vs seconds)

## Security Considerations

### 1. File Operations

- Path traversal vulnerability in output path handling
- No sanitization of file names
- Potential shell injection in FFmpeg parameters
- Temporary file permissions not restricted
- No limits on concurrent operations

### 2. API Security

- API key handling could be improved
- No rate limiting implementation
- Missing request validation
- No audit logging of operations
- Credentials in environment variables need better documentation

## Code Quality Improvements

### 1. Testing

- Missing unit tests
- No integration tests
- No performance benchmarks
- No error scenario testing
- Missing mock implementations for FFmpeg

### 2. Documentation

- Missing JSDoc for many functions
- No API documentation
- Limited error code documentation
- No troubleshooting guide
- Missing architecture diagrams

### 3. Maintainability

```typescript
// Example of current implementation
async function processGenerationAttempt(
  model: GoogleGenerativeAI,
  fileManager: GoogleAIFileManager,
  modelName: string,
  prompt: string,
  files: FileInput[],
  temperature: number = 0,
  schema?: any
): Promise<GeminiResponse>;
```

Could be improved with:

- Better separation of concerns
- More modular design
- Configuration object pattern
- Consistent error handling
- Better type safety

## Specific Bug Fixes Needed

1. `utils/audio-chunk.ts`:

```typescript
function getFileDuration(filePath: string): Promise<number> {
  return new Promise((resolve, reject) => {
    ffmpeg.ffprobe(filePath, (err, metadata) => {
      if (err) reject(err);
      resolve(metadata.format.duration || 0); // Bug: Could resolve with 0 silently
    });
  });
}
```

2. `utils/screenshot.ts`:

```typescript
const startTime = duration * 0.01;
const endTime = duration * 0.99;
// Bug: No check for very short videos where this could result in invalid timestamps
```

3. `src/describe.ts`:

```typescript
if (screenshotBar) screenshotBar.update(50);
// Bug: Hard-coded progress values don't reflect actual progress
```

4. `src/transcribe.ts`:

```typescript
let previousTranscription = getLastNLines(transcriptionText, 20);
// Bug: Magic number and no consideration for very short lines
```

## Recommendations for Next Steps

1. Immediate Fixes:

- Implement proper cleanup handlers
- Add input validation
- Improve error handling
- Add basic security measures

2. Short-term Improvements:

- Add comprehensive testing
- Implement logging
- Add performance monitoring
- Improve documentation

## Best Practices to Implement

1. Code Organization:

- Consistent error handling
- Better type safety
- Clear naming conventions
- Proper separation of concerns

2. Operations:

- Proper logging
- Monitoring
- Resource management
- Error tracking

3. Security:

- Input validation
- Output sanitization
- Proper file permissions
- Rate limiting

Any of these are up for grabs to implement!


================================================
File: TODO.md
================================================
1. Redo the description and summary and question answers. See if we can't generate a full doc?
2. Counting tokens and reporting back
3. Trying to merge whisper transcriptions?
4. Make more intelligent screenshots
5. (Bug) We're making a transcription folder next to the video file for some reason. Need to fix!


================================================
File: package.json
================================================
{
  "name": "offmute",
  "version": "0.0.5",
  "author": "Hrishi Olickel <twitter-@hrishioa> (https://olickel.com)",
  "repository": {
    "type": "git",
    "url": "git+https://github.com/southbridgeai/offmute.git"
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "bin": {
    "offmute": "./dist/run.js"
  },
  "devDependencies": {
    "@swc/core": "^1.7.40",
    "@types/bun": "^1.1.12",
    "@types/node": "^22.8.4",
    "tsup": "^8.3.5",
    "typescript": "^5.6.3"
  },
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.js"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    }
  },
  "description": "An experiment in meeting transcription and diarization with just an LLM.",
  "files": [
    "dist",
    "package.json"
  ],
  "license": "Apache-2.0",
  "scripts": {
    "build": "tsup src/index.ts src/run.ts && tsc --emitDeclarationOnly --declaration --declarationDir dist && mv dist/index.d.ts dist/index.d.mts && cp dist/index.d.mts dist/index.d.cts"
  },
  "type": "module",
  "types": "./dist/index.d.cts",
  "dependencies": {
    "@google/generative-ai": "^0.21.0",
    "chalk": "^5.3.0",
    "cli-progress": "^3.12.0",
    "commander": "^12.1.0",
    "fluent-ffmpeg": "^2.1.3"
  }
}


================================================
File: tsconfig.json
================================================
{
  "ts-node": {
    "files": true
  },
  "compilerOptions": {
    "baseUrl": ".",
    "target": "es2020",
    "module": "esnext",
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "strictPropertyInitialization": false,
    "skipLibCheck": true,
    // "strictNullChecks": true,
    "strictBindCallApply": false,
    "declaration": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "allowSyntheticDefaultImports": true,
    "moduleResolution": "node",
    "sourceMap": true,
    "outDir": "./dist",
    "noImplicitAny": false,
    "noFallthroughCasesInSwitch": false,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"]
}


================================================
File: tsup.config.ts
================================================
import { defineConfig } from "tsup";

export default defineConfig([
  // Build for the package (importable)
  {
    entry: ["src/index.ts"],
    format: ["cjs", "esm"],
    dts: true,
    splitting: false,
    sourcemap: true,
    clean: true,
    outDir: "dist",
    outExtension({ format }) {
      return {
        js: format === "cjs" ? ".cjs" : ".js",
      };
    },
  },
  // Build for the CLI
  {
    entry: ["src/run.ts"],
    format: ["esm"],
    sourcemap: true,
    clean: false,
    outDir: "dist",
    banner: {
      js: "#!/usr/bin/env node",
    },
  },
]);


================================================
File: .npmignore
================================================
archive
tests

.DS_Store
zig-cache
packages/*/*.wasm
*.o
*.a
profile.json

.env
node_modules
.envrc
.swcrc
yarn.lock
*.tmp
*.log
*.out.js
*.out.refresh.js
**/package-lock.json
build
*.wat
zig-out
pnpm-lock.yaml
README.md.template
src/deps/zig-clap/example
src/deps/zig-clap/README.md
src/deps/zig-clap/.github
src/deps/zig-clap/.gitattributes
out
outdir

.trace
cover
coverage
coverv
*.trace
github
out.*
out
.parcel-cache
esbuilddir
*.bun
parceldist
esbuilddir
outdir/
outcss
.next
txt.js
.idea
.vscode/cpp*
.vscode/clang*

node_modules_*
*.jsb
*.zip
bun-zigld
bun-singlehtreaded
bun-nomimalloc
bun-mimalloc
examples/lotta-modules/bun-yday
examples/lotta-modules/bun-old
examples/lotta-modules/bun-nofscache

src/node-fallbacks/out/*
src/node-fallbacks/node_modules
sign.json
release/
*.dmg
sign.*.json
packages/debug-*
packages/bun-cli/postinstall.js
packages/bun-*/bun
packages/bun-*/bun-profile
packages/bun-*/debug-bun
packages/bun-*/*.o
packages/bun-cli/postinstall.js

packages/bun-cli/bin/*
bun-test-scratch
misctools/fetch

src/deps/libiconv
src/deps/openssl
src/tests.zig
*.blob
src/deps/s2n-tls
.npm
.npm.gz

bun-binary

src/deps/PLCrashReporter/

*.dSYM
*.crash
misctools/sha
packages/bun-wasm/*.mjs
packages/bun-wasm/*.cjs
packages/bun-wasm/*.map
packages/bun-wasm/*.js
packages/bun-wasm/*.d.ts
packages/bun-wasm/*.d.cts
packages/bun-wasm/*.d.mts
*.bc

src/fallback.version
src/runtime.version
*.sqlite
*.database
*.db
misctools/machbench
*.big
.eslintcache

/bun-webkit

src/deps/c-ares/build
src/bun.js/bindings-obj
src/bun.js/debug-bindings-obj

failing-tests.txt
test.txt
myscript.sh

cold-jsc-start
cold-jsc-start.d

/testdir
/test.ts
/test.js

src/js/out/modules*
src/js/out/functions*
src/js/out/tmp
src/js/out/DebugPath.h

make-dev-stats.csv

.uuid
tsconfig.tsbuildinfo

test/js/bun/glob/fixtures
*.lib
*.pdb
CMakeFiles
build.ninja
.ninja_deps
.ninja_log
CMakeCache.txt
cmake_install.cmake
compile_commands.json

*.lib
x64
**/*.vcxproj*
**/*.sln*
**/*.dir
**/*.pdb

/.webkit-cache
/.cache
/src/deps/libuv
/build-*/
/kcov-out

.vs

**/.verdaccio-db.json
/test-report.md
/test-report.json

########################### MY STUFF

tests

================================================
File: src/describe.ts
================================================
import path from "path";
import fs from "fs";
import { processAudioFile } from "./utils/audio-chunk";
import { extractVideoScreenshots } from "./utils/screenshot";
import { generateWithGemini } from "./utils/gemini";
import {
  AUDIO_DESC_PROMPT,
  IMAGE_DESC_PROMPT,
  MERGE_DESC_PROMPT,
} from "./prompts";
import { SingleBar, Presets, MultiBar } from "cli-progress";
import { isVideoFile } from "./utils/check-type";

interface GenerateDescriptionOptions {
  screenshotModel: string;
  screenshotCount?: number;
  audioModel: string;
  descriptionChunkMinutes?: number;
  transcriptionChunkMinutes?: number;
  mergeModel: string;
  outputPath?: string;
  showProgress?: boolean;
}

export interface GenerateDescriptionResult {
  imageDescription?: string;
  audioDescription?: string;
  finalDescription: string;
  generatedFiles: {
    screenshots: string[];
    audioChunks: string[];
    intermediateOutputPath?: string;
  };
}

interface IntermediateOutput {
  timestamp: number;
  prompt?: string;
  imageDescription?: string;
  audioDescription?: string;
  finalDescription?: string;
  error?: string;
}

async function saveIntermediateOutput(
  outputPath: string | undefined,
  data: Partial<IntermediateOutput>
): Promise<void> {
  if (!outputPath) return;

  const outputFile = path.join(outputPath, "intermediate_output.json");
  const timestamp = Date.now();

  // Create directory if it doesn't exist
  if (!fs.existsSync(outputPath)) {
    fs.mkdirSync(outputPath, { recursive: true });
  }

  // Read existing data if it exists
  let existingData: IntermediateOutput[] = [];
  if (fs.existsSync(outputFile)) {
    try {
      existingData = JSON.parse(fs.readFileSync(outputFile, "utf8"));
    } catch (error) {
      console.warn("Error reading intermediate output file:", error);
    }
  }

  // Add new data
  existingData.push({
    timestamp,
    ...data,
  });

  // Save updated data
  fs.writeFileSync(outputFile, JSON.stringify(existingData, null, 2));
}

export async function generateDescription(
  inputFile: string,
  options: GenerateDescriptionOptions
): Promise<GenerateDescriptionResult> {
  const {
    screenshotModel,
    screenshotCount = 4,
    audioModel,
    descriptionChunkMinutes = 20,
    transcriptionChunkMinutes = 10,
    mergeModel,
    outputPath,
    showProgress = false,
  } = options;

  // Initialize progress bars if needed
  let multibar: MultiBar | undefined;
  let screenshotBar: SingleBar | undefined;
  let audioBar: SingleBar | undefined;
  let processingBar: SingleBar | undefined;

  if (showProgress) {
    multibar = new MultiBar(
      {
        format: "{bar} | {percentage}% | {task}",
        hideCursor: true,
      },
      Presets.shades_classic
    );

    // Only create progress bars for relevant operations
    if (isVideoFile(inputFile)) {
      screenshotBar = multibar.create(100, 0, { task: "Screenshots" });
    }
    audioBar = multibar.create(100, 0, { task: "Audio Processing" });
    processingBar = multibar.create(100, 0, { task: "AI Processing" });
  }

  try {
    // Determine which operations to run based on file type
    const isVideo = isVideoFile(inputFile);

    // Start parallel processing of screenshots (if video) and audio
    const [screenshotResult, audioResult] = await Promise.all([
      // Generate screenshots only if it's a video file
      isVideo
        ? extractVideoScreenshots(inputFile, {
            screenshotCount,
            outputDir: outputPath
              ? path.join(outputPath, "screenshots")
              : undefined,
          }).then(async (screenshots) => {
            if (screenshotBar) screenshotBar.update(50);

            const imageDescription = await generateWithGemini(
              screenshotModel,
              IMAGE_DESC_PROMPT(screenshots.map((s) => s.path).join(", ")),
              screenshots.map((s) => ({ path: s.path }))
            );

            if (screenshotBar) screenshotBar.update(100);

            await saveIntermediateOutput(outputPath, {
              imageDescription: imageDescription.text,
            });

            return {
              description: imageDescription.text,
              files: screenshots.map((s) => s.path),
            };
          })
        : Promise.resolve({ description: "", files: [] }),

      // Process audio
      processAudioFile(inputFile, {
        chunkMinutes: transcriptionChunkMinutes,
        tagMinutes: descriptionChunkMinutes,
        outputDir: outputPath ? path.join(outputPath, "audio") : undefined,
      }).then(async (chunks) => {
        if (audioBar) audioBar.update(50);

        const audioDescription = await generateWithGemini(
          audioModel,
          AUDIO_DESC_PROMPT(path.basename(inputFile)),
          [{ path: chunks.tagSample }]
        );

        if (audioBar) audioBar.update(100);

        await saveIntermediateOutput(outputPath, {
          audioDescription: audioDescription.text,
        });

        return {
          description: audioDescription.text,
          files: chunks.chunks.map((c) => c.path),
        };
      }),
    ]);

    if (processingBar) processingBar.update(50);

    // Adjust merge prompt based on available descriptions
    const descriptionsToMerge = isVideo
      ? [screenshotResult.description, audioResult.description]
      : [audioResult.description];

    const finalDescription = await generateWithGemini(
      mergeModel,
      MERGE_DESC_PROMPT(descriptionsToMerge),
      []
    );

    if (processingBar) processingBar.update(100);

    await saveIntermediateOutput(outputPath, {
      prompt: MERGE_DESC_PROMPT(descriptionsToMerge),
      finalDescription: finalDescription.text,
    });

    // Clean up progress bars
    if (multibar) {
      multibar.stop();
    }

    return {
      imageDescription: isVideo ? screenshotResult.description : undefined,
      audioDescription: audioResult.description,
      finalDescription: finalDescription.text,
      generatedFiles: {
        screenshots: screenshotResult.files,
        audioChunks: audioResult.files,
        intermediateOutputPath: outputPath,
      },
    };
  } catch (error) {
    // Save error state if output path is provided
    if (outputPath) {
      await saveIntermediateOutput(outputPath, {
        error: error instanceof Error ? error.message : String(error),
      });
    }

    // Clean up progress bars
    if (multibar) {
      multibar.stop();
    }

    throw error;
  }
}

// Example usage:
// const result = await generateDescription(
//   __dirname + "/../tests/data/speech.mp3",
//   {
//     screenshotModel: "gemini-1.5-flash-8b",
//     screenshotCount: 6,
//     audioModel: "gemini-1.5-flash-8b",
//     descriptionChunkMinutes: 20,
//     transcriptionChunkMinutes: 1,
//     mergeModel: "gemini-1.5-flash-8b",
//     outputPath: __dirname + "/../tests/description_tests",
//     showProgress: true,
//   }
// );

// console.log("Final Description:", result.finalDescription);


================================================
File: src/index.ts
================================================
export { generateDescription } from "./describe";
export { generateTranscription } from "./transcribe";
export { generateReport } from "./report";


================================================
File: src/prompts.ts
================================================
// prettier-ignore
export const AUDIO_DESC_PROMPT = (fileName: string) =>
`Describe this audio in two paragraphs with the following information:

1. What are the key topics of discussion?
2. Who are the people talking to the best of your knowledge? Describe them, names if possible at all, and their personalities, job functions, etc. Identify them with speaker 1 and 2 if you don't have names.
3. Summarise this conversation in three sentences, like 'This is a discussion between X (who Y) and X (who Y) about ....'

File: ${fileName}`

// prettier-ignore
export const IMAGE_DESC_PROMPT = (fileNames: string) =>
`Provided are some screenshots from a meeting. Can you provide the following information from the image (when available)?

1. Who the speakers are (if you can see them), their names, descriptions.
2. General emotions of the people involved.
3. Descriptions of anything else shown on the screen or being shared.
4. Any additional information you can infer about the meeting from the  information provided.

The files are: ${fileNames}`

// prettier-ignore
export const MERGE_DESC_PROMPT = (descriptions: string[]) =>
`
Descriptions:
\`\`\`
${descriptions.join("\n\n")}
\`\`\`

Here are the descriptions for a meeting, generated from information (audio/images, etc) about it. Remove conflicting information, use your best judgement to infer what happened, and generate a clean, detailed description for the meeting covering the following:
1. Who the participants of the meeting were. Names if possible.
2. Describe the participants. Appearance if possible, function, emotional state, job, etc.
3. What was discussed? What was shown/covered?
4. If this is not a meeting, provide any additional information that can help describe what this is.`

// prettier-ignore
export const TRANSCRIPTION_PROMPT = (description: string, count: number, total: number, previousTranscription: string) =>
`Provided is (${count}/${total}) of the audio of a meeting.

Here is the general description of the meeting:
${description}

${previousTranscription ?
`Here is the transcription from the previous chunk:\n\n...${previousTranscription}\n...` : ""}

Please diarize and transcribe this audio segment with all the speakers identified and named when possible. Format the output as:
~[Speaker Name]~: Transcribed text

${previousTranscription ?
`Continue where the previous transcription left off.` : ""}`

// prettier-ignore
export const REPORT_HEADINGS_PROMPT = (descriptions: string, transcript: string) =>
`Meeting Descriptions:
\`\`\`
${descriptions}
\`\`\`

Transcript:
\`\`\`
${transcript}
\`\`\`

Here are the descriptions and transcript of a meeting or call. We want to turn this into a proper one-pager summary document. Respond with json in this typespec representing the headings and subheadings of the final one-page report, with a one-sentence description. Some things to make sure we cover (in their own section or not) are:
* Useful contacts - companies, people etc
* Action items
* Overall flow of the meeting - what was discussed for how long
* Any arguments or pitches made or things presented
* Participant profiles

Respond with json in this typespec:
\`\`\`typescript
type MeetingSummary = {
  sections: {
    title: string;
    description: string;
    subsections: {
      title: string;
      description: string;
    }[]
  }[];
}
\`\`\``

export type ReportHeadings = {
  sections: ReportSection[];
};

export type ReportSection = {
  title: string;
  description: string;
  subsections: {
    title: string;
    description: string;
  }[];
};

export const REPORT_HEADINGS_JSONSCHEMA = {
  type: "object",
  description: "Meeting report headings and subheadings",
  properties: {
    sections: {
      type: "array",
      items: {
        type: "object",
        properties: {
          title: {
            type: "string",
          },
          description: {
            type: "string",
          },
          subsections: {
            type: "array",
            items: {
              type: "object",
              properties: {
                title: {
                  type: "string",
                },
                description: {
                  type: "string",
                },
              },
              required: ["title", "description"],
            },
          },
        },
        required: ["title", "description", "subsections"],
      },
    },
  },
  required: ["sections"],
};

// prettier-ignore
export const REPORT_SECTION_GENERATION_PROMPT = (headings: ReportHeadings, section: ReportSection, transcript: string, descriptions: string) =>
`Meeting Descriptions:
\`\`\`
${descriptions}
\`\`\`

Transcript:
\`\`\`
${transcript}
\`\`\`

Here are the descriptions and transcript of a meeting or call. We want to turn this into a proper one-pager summary document. Respond with json representing the headings and subheadings of the final one-page report.

Here are the main sections we want in the report:
${headings.sections.map((sectionName, index) => `${index + 1}. ${sectionName.title} : ${sectionName.description}`).join("\n")}

We want to write this specific section in markdown:
${section.title}: ${section.description}

Respond with just the content for this section, without title or description or foreword or introduction. Presume the other sections have been written.

Respond in Markdown.
`


================================================
File: src/report.ts
================================================
import { generateWithGemini } from "./utils/gemini";
import {
  REPORT_HEADINGS_JSONSCHEMA,
  REPORT_HEADINGS_PROMPT,
  REPORT_SECTION_GENERATION_PROMPT,
  ReportHeadings,
  ReportSection,
} from "./prompts";
import path from "path";
import fs from "fs";

interface GenerateReportOptions {
  model: string;
  outputPath: string;
  reportName: string;
  showProgress?: boolean;
}

interface GenerateReportResult {
  reportPath: string;
  sections: ReportSection[];
  intermediateOutputPath: string;
}

interface ReportGenerationOutput {
  timestamp: number;
  step: string;
  data: any;
  prompt?: string;
  error?: string;
}

function isValidSectionContent(content: string): boolean {
  // Check if content appears to be JSON
  if (content.trim().startsWith("{") || content.trim().startsWith("[")) {
    try {
      JSON.parse(content);
      return false; // If it parses as JSON, it's not valid section content
    } catch {
      // If it doesn't parse as JSON, continue with other checks
    }
  }

  // Check if content is too short or empty
  if (content.trim().length < 10) {
    return false;
  }

  // Check if content appears to be just headings
  const contentLines = content.trim().split("\n");
  if (
    contentLines.every((line) => line.startsWith("#") || line.trim() === "")
  ) {
    return false;
  }

  return true;
}

async function saveReportOutput(
  outputPath: string,
  data: Partial<ReportGenerationOutput>
): Promise<void> {
  const outputFile = path.join(outputPath, "report_generation.json");
  const timestamp = Date.now();

  // Create directory if it doesn't exist
  if (!fs.existsSync(outputPath)) {
    fs.mkdirSync(outputPath, { recursive: true });
  }

  // Read existing data if it exists
  let existingData: ReportGenerationOutput[] = [];
  if (fs.existsSync(outputFile)) {
    try {
      existingData = JSON.parse(fs.readFileSync(outputFile, "utf8"));
    } catch (error) {
      console.warn("Error reading report generation file:", error);
    }
  }

  // Add new data
  existingData.push({
    timestamp,
    ...data,
  } as ReportGenerationOutput);

  // Save updated data
  fs.writeFileSync(outputFile, JSON.stringify(existingData, null, 2));
}

export async function generateReport(
  descriptions: string,
  transcript: string,
  options: GenerateReportOptions
): Promise<GenerateReportResult> {
  const { model, outputPath, reportName, showProgress = false } = options;

  // Create report directory under outputPath
  const reportDir = path.join(outputPath, "report");
  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
  }

  try {
    if (showProgress) {
      console.log("Generating report structure...");
    }

    // Save initial prompts
    const headingsPrompt = REPORT_HEADINGS_PROMPT(descriptions, transcript);
    await saveReportOutput(reportDir, {
      step: "initial_prompt",
      prompt: headingsPrompt,
      data: {
        descriptions,
        transcript,
      },
    });

    // First, generate the report structure
    const headingsResponse = await generateWithGemini(
      model,
      headingsPrompt,
      [],
      {
        maxRetries: 3,
        temperature: 0.2,
        schema: REPORT_HEADINGS_JSONSCHEMA,
      }
    );

    if (headingsResponse.error) {
      throw new Error(
        `Failed to generate report structure: ${headingsResponse.error}`
      );
    }

    await saveReportOutput(reportDir, {
      step: "generate_structure",
      data: headingsResponse.text,
    });

    const headings: ReportHeadings = JSON.parse(headingsResponse.text);

    if (showProgress) {
      console.log(`Generating ${headings.sections.length} sections...`);
    }

    // Generate content for each section
    const sectionContents: string[] = [];
    for (let i = 0; i < headings.sections.length; i++) {
      const section = headings.sections[i];

      if (showProgress) {
        console.log(
          `Processing section ${i + 1}/${headings.sections.length}: ${
            section.title
          }`
        );
      }

      try {
        const sectionPrompt = REPORT_SECTION_GENERATION_PROMPT(
          headings,
          section,
          transcript,
          descriptions
        );

        // Save section prompt
        await saveReportOutput(reportDir, {
          step: "section_prompt",
          prompt: sectionPrompt,
          data: {
            sectionTitle: section.title,
            sectionIndex: i,
          },
        });

        const sectionResponse = await generateWithGemini(
          model,
          sectionPrompt,
          [],
          {
            maxRetries: 3,
            temperature: 0.3,
          }
        );

        if (
          sectionResponse.error ||
          !isValidSectionContent(sectionResponse.text)
        ) {
          console.warn(
            `Warning: Error or invalid content for section ${section.title}: ${
              sectionResponse.error || "Invalid content format"
            }`
          );

          // Retry once with a more explicit prompt if content was invalid
          if (
            !sectionResponse.error &&
            !isValidSectionContent(sectionResponse.text)
          ) {
            const retryPrompt = `${sectionPrompt}\n\nPlease provide the content for this section in plain text format, not as JSON or outline. Write it as a narrative paragraph.`;

            const retryResponse = await generateWithGemini(
              model,
              retryPrompt,
              [],
              {
                maxRetries: 2,
                temperature: 0.3,
              }
            );

            if (
              !retryResponse.error &&
              isValidSectionContent(retryResponse.text)
            ) {
              sectionContents.push(
                `## ${section.title}\n\n${retryResponse.text}`
              );
            }
          }
        } else {
          sectionContents.push(
            `## ${section.title}\n\n${sectionResponse.text}`
          );
        }

        await saveReportOutput(reportDir, {
          step: "generate_section",
          data: {
            section: section.title,
            content: sectionResponse.text,
            error: sectionResponse.error,
          },
        });
      } catch (error) {
        console.warn(
          `Warning: Failed to generate section ${section.title}:`,
          error
        );
        sectionContents.push(
          `## ${section.title}\n\n*Error generating content*`
        );
      }
    }

    // Combine all sections into final report
    const reportContent = ["# Meeting Report\n", ...sectionContents].join(
      "\n\n"
    );

    // Save the report with custom name
    const reportPath = path.join(outputPath, `${reportName}.md`);
    fs.writeFileSync(reportPath, reportContent, "utf-8");

    if (showProgress) {
      console.log(`Report generation complete. Saved to: ${reportPath}`);
    }

    return {
      reportPath,
      sections: headings.sections,
      intermediateOutputPath: reportDir,
    };
  } catch (error) {
    // Save error state
    await saveReportOutput(reportDir, {
      step: "error",
      error: error instanceof Error ? error.message : String(error),
      data: null,
    });

    throw error;
  }
}

// const result = await generateReport(descriptions, transcript, {
//   model: "gemini-1.5-pro",
//   outputPath: __dirname + "/../tests/report_tests",
//   reportName: "test_meeting",
//   showProgress: true,
// });

// console.log("Report saved to:", result.reportPath);
// console.log("Intermediates saved to:", result.intermediateOutputPath);


================================================
File: src/run.ts
================================================
#!/usr/bin/env node
import { Command } from "commander";
import path from "path";
import fs from "fs";
import ffmpeg from "fluent-ffmpeg";
import chalk from "chalk";

import { generateDescription } from "./describe";
import { generateTranscription } from "./transcribe";
import { generateReport } from "./report";
import { isAudioFile, isVideoFile } from "./utils/check-type";
import { checkFFmpeg } from "./utils/ffmpeg-check";

const MODEL_TIERS = {
  first: {
    description: "gemini-2.0-pro-exp-02-05",
    transcription: "gemini-2.0-pro-exp-02-05",
    report: "gemini-2.0-pro-exp-02-05",
    label: "First Tier (Pro models)",
  },
  business: {
    description: "gemini-2.0-pro-exp-02-05",
    transcription: "gemini-2.0-flash",
    report: "gemini-2.0-pro-exp-02-05",
    label: "Business Tier (Pro for description, Flash for transcription)",
  },
  economy: {
    description: "gemini-2.0-flash",
    transcription: "gemini-2.0-flash",
    report: "gemini-2.0-flash",
    label: "Economy Tier (Flash models)",
  },
  budget: {
    description: "gemini-2.0-flash",
    transcription: "gemini-2.0-flash-lite-preview-02-05",
    report: "gemini-2.0-flash-lite-preview-02-05",
    label: "Budget Tier (Flash for description, Flash Lite for transcription)",
  },
} as const;

function getVideoDuration(filePath: string): Promise<number> {
  return new Promise((resolve, reject) => {
    ffmpeg.ffprobe(filePath, (err, metadata) => {
      if (err) reject(err);
      resolve(metadata.format.duration || 0);
    });
  });
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  const parts: string[] = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  parts.push(`${remainingSeconds}s`);

  return parts.join(" ");
}

async function findFiles(dir: string): Promise<string[]> {
  const files: string[] = [];

  const items = fs.readdirSync(dir);
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      files.push(...(await findFiles(fullPath)));
    } else if (isVideoFile(fullPath) || isAudioFile(fullPath)) {
      files.push(fullPath);
    }
  }

  return files;
}

async function processFile(
  inputFile: string,
  tier: keyof typeof MODEL_TIERS,
  saveIntermediates: boolean,
  screenshotCount: number,
  audioChunkMinutes: number,
  generateReports: boolean,
  reportsDir?: string
): Promise<void> {
  const inputBaseName = path.basename(inputFile, path.extname(inputFile));
  const outputDir = saveIntermediates
    ? path.join(path.dirname(inputFile), `${inputBaseName}_intermediates`)
    : undefined;

  const startTime = Date.now();
  console.log(`\nProcessing: ${inputFile}`);
  console.log(`Using: ${MODEL_TIERS[tier].label}`);

  try {
    const videoDuration = await getVideoDuration(inputFile);

    const descriptionResult = await generateDescription(inputFile, {
      screenshotModel: MODEL_TIERS[tier].description,
      screenshotCount,
      audioModel: MODEL_TIERS[tier].description,
      transcriptionChunkMinutes: audioChunkMinutes,
      mergeModel: MODEL_TIERS[tier].description,
      outputPath: outputDir,
      showProgress: true,
    });

    const transcriptionResult = await generateTranscription(
      inputFile,
      descriptionResult,
      {
        transcriptionModel: MODEL_TIERS[tier].transcription,
        outputPath: path.dirname(inputFile),
        showProgress: true,
      }
    );

    // Generate report if requested
    if (generateReports) {
      console.log("Generating meeting report...");

      // Determine report output path
      const reportOutputPath = reportsDir || path.dirname(inputFile);

      const reportResult = await generateReport(
        descriptionResult.finalDescription,
        transcriptionResult.chunkTranscriptions.join("\n\n"),
        {
          model: MODEL_TIERS[tier].report,
          outputPath: reportOutputPath,
          reportName: `${inputBaseName}_report`,
          showProgress: true,
        }
      );

      console.log(`Report saved to: ${reportResult.reportPath}`);
    }

    const totalSeconds = (Date.now() - startTime) / 1000;
    const timePerMinute = totalSeconds / (videoDuration / 60);

    console.log(
      `Complete in ${formatDuration(totalSeconds)} (${timePerMinute.toFixed(
        1
      )}s per minute)`
    );
    console.log(`Transcription: ${transcriptionResult.transcriptionPath}`);
  } catch (error) {
    console.error(
      chalk.red(`Error processing ${inputFile}:`),
      error instanceof Error ? error.message : String(error)
    );
    throw error;
  }
}

async function run() {
  // First check for FFmpeg
  const ffmpegAvailable = await checkFFmpeg();
  if (!ffmpegAvailable) {
    process.exit(1);
  }

  if (!process.env.GEMINI_API_KEY) {
    console.error(chalk.red.bold("\n❌ Missing API Key"));
    console.error(
      chalk.yellow(
        "\nPlease set your GEMINI_API_KEY in the environment to use offmute."
      )
    );
    process.exit(1);
  }

  const program = new Command();

  program
    .argument("<input>", "Input video file or directory path")
    .option(
      "-t, --tier <tier>",
      "Processing tier (first, business, economy, budget)",
      "business"
    )
    .option(
      "-a, --all",
      "Save all intermediate outputs in separate folders",
      false
    )
    .option(
      "-sc, --screenshot-count <number>",
      "Number of screenshots to extract",
      "4"
    )
    .option(
      "-ac, --audio-chunk-minutes <number>",
      "Length of audio chunks in minutes",
      "10"
    )
    .option("-r, --report", "Generate a structured meeting report", false)
    .option(
      "-rd, --reports-dir <path>",
      "Custom directory for report output (defaults to input file location)"
    )
    .version("1.0.0");

  program.parse();

  console.log(
    chalk.cyan(
      "⭐ Welcome to offmute - built by Hrishi (https://twitter.com/hrishioa) and named by Ben (https://twitter.com/bencmejla) ⭐"
    )
  );

  const options = program.opts();
  const input = program.args[0];

  if (!input || !MODEL_TIERS[options.tier as keyof typeof MODEL_TIERS]) {
    console.error(chalk.red("Error: Invalid input path or tier selection"));
    console.log(chalk.yellow("\nAvailable tiers:"));
    Object.entries(MODEL_TIERS).forEach(([key, value]) => {
      console.log(chalk.cyan(`- ${key}: ${value.label}`));
    });
    process.exit(1);
  }

  // Create reports directory if specified
  if (options.reportsDir) {
    fs.mkdirSync(options.reportsDir, { recursive: true });
  }

  const stats = fs.statSync(input);
  const files = stats.isDirectory() ? await findFiles(input) : [input];

  if (files.length === 0) {
    console.error(chalk.red("No video files found"));
    process.exit(1);
  }

  console.log(
    chalk.green(
      `Found ${files.length} video file${
        files.length > 1 ? "s" : ""
      } to process`
    )
  );

  const startTime = Date.now();
  const results = {
    success: 0,
    failed: 0,
    failedFiles: [] as string[],
  };

  for (const file of files) {
    try {
      await processFile(
        file,
        options.tier as keyof typeof MODEL_TIERS,
        options.all,
        parseInt(options.screenshotCount),
        parseInt(options.audioChunkMinutes),
        options.report,
        options.reportsDir
      );
      results.success++;
    } catch (error) {
      results.failed++;
      results.failedFiles.push(file);
    }
  }

  const totalTime = (Date.now() - startTime) / 1000;

  console.log(chalk.cyan("\nProcessing Summary:"));
  console.log(chalk.white(`Total time: ${formatDuration(totalTime)}`));
  console.log(
    chalk.green(`Successfully processed: ${results.success}/${files.length}`)
  );

  if (results.failed > 0) {
    console.log(chalk.red("\nFailed files:"));
    results.failedFiles.forEach((file) =>
      console.log(chalk.yellow(`- ${file}`))
    );
    process.exit(1);
  } else if (results.success > 0) {
    console.log(
      chalk.cyan(
        "\n🌟 If that worked, consider starring https://github.com/southbridgeai/offmute !"
      )
    );
    console.log(chalk.cyan("    https://github.com/southbridgeai/offmute"));
  }
}

process.on("unhandledRejection", (error) => {
  console.error(chalk.red("Fatal Error:"), error);
  process.exit(1);
});

run();


================================================
File: src/transcribe.ts
================================================
import path from "path";
import fs from "fs";
import { generateDescription, GenerateDescriptionResult } from "./describe";
import { generateWithGemini } from "./utils/gemini";
import { TRANSCRIPTION_PROMPT } from "./prompts";

interface TranscriptionOptions {
  transcriptionModel: string;
  outputPath?: string;
  showProgress?: boolean;
}

interface TranscriptionResult {
  transcriptionPath: string;
  chunkTranscriptions: string[];
  intermediateOutputPath?: string;
}

interface TranscriptionChunkOutput {
  timestamp: number;
  chunkIndex: number;
  prompt: string;
  response: string;
  error?: string;
}

async function saveTranscriptionOutput(
  outputPath: string,
  data: TranscriptionChunkOutput
): Promise<void> {
  const outputFile = path.join(outputPath, "transcription_progress.json");
  const existingData: TranscriptionChunkOutput[] = [];

  // Read existing data if it exists
  if (fs.existsSync(outputFile)) {
    try {
      const content = fs.readFileSync(outputFile, "utf8");
      Object.assign(existingData, JSON.parse(content));
    } catch (error) {
      console.warn("Error reading transcription progress file:", error);
    }
  }

  // Add or update chunk data
  const existingIndex = existingData.findIndex(
    (item) => item.chunkIndex === data.chunkIndex
  );

  if (existingIndex >= 0) {
    existingData[existingIndex] = data;
  } else {
    existingData.push(data);
  }

  // Sort by chunk index
  existingData.sort((a, b) => a.chunkIndex - b.chunkIndex);

  // Save updated data
  fs.writeFileSync(outputFile, JSON.stringify(existingData, null, 2));
}

// Helper function to get last N lines of text
function getLastNLines(text: string, n: number): string {
  if (!text) return "";
  const lines = text.split("\n").filter((line) => line.trim());
  return lines.slice(-n).join("\n");
}

export async function generateTranscription(
  inputFile: string,
  descriptionResult: GenerateDescriptionResult,
  options: TranscriptionOptions
): Promise<TranscriptionResult> {
  const {
    transcriptionModel,
    outputPath = path.dirname(inputFile),
    showProgress = false,
  } = options;

  // Create output directory if it doesn't exist
  if (!fs.existsSync(outputPath)) {
    fs.mkdirSync(outputPath, { recursive: true });
  }

  // Save initial prompt templates and configuration
  const configOutput = {
    timestamp: Date.now(),
    inputFile,
    model: transcriptionModel,
    description: descriptionResult.finalDescription,
    audioDescription: descriptionResult.audioDescription,
    imageDescription: descriptionResult.imageDescription,
    chunkCount: descriptionResult.generatedFiles.audioChunks.length,
  };

  // Save config.json in the main intermediates directory
  const configPath = path.join(
    descriptionResult.generatedFiles.intermediateOutputPath || outputPath,
    "config.json"
  );

  fs.writeFileSync(configPath, JSON.stringify(configOutput, null, 2));

  const chunks = descriptionResult.generatedFiles.audioChunks;
  const chunkCount = chunks.length;
  const chunkTranscriptions: string[] = [];

  // Initialize progress tracking if needed
  if (showProgress) {
    console.log(`Starting transcription of ${chunkCount} chunks...`);
  }

  // Create transcription directory in the same intermediates folder
  const transcriptionDir = path.join(
    descriptionResult.generatedFiles.intermediateOutputPath || outputPath,
    "transcription"
  );
  if (!fs.existsSync(transcriptionDir)) {
    fs.mkdirSync(transcriptionDir, { recursive: true });
  }

  // Process chunks sequentially to maintain context
  let previousTranscription = "";
  for (let i = 0; i < chunkCount; i++) {
    if (showProgress) {
      console.log(`Processing chunk ${i + 1}/${chunkCount}`);
    }

    const chunk = chunks[i];
    const prompt = TRANSCRIPTION_PROMPT(
      descriptionResult.finalDescription,
      i + 1,
      chunkCount,
      previousTranscription
    );

    try {
      const transcriptionResponse = await generateWithGemini(
        transcriptionModel,
        prompt,
        [{ path: chunk }],
        {
          maxRetries: 3,
          temperature: 0.2, // Lower temperature for more consistent transcription
        }
      );

      // Save chunk progress including prompt and response
      await saveTranscriptionOutput(transcriptionDir, {
        timestamp: Date.now(),
        chunkIndex: i,
        prompt,
        response: transcriptionResponse.text,
        error: transcriptionResponse.error,
      });

      if (transcriptionResponse.error) {
        console.error(
          `Error transcribing chunk ${i + 1}:`,
          transcriptionResponse.error
        );
        chunkTranscriptions.push(
          `\n[Transcription error for chunk ${i + 1}]\n`
        );
      } else {
        // Clean up the transcription text
        let transcriptionText = transcriptionResponse.text.trim();

        // Add spacing between speakers if not present
        transcriptionText = transcriptionText.replace(/~\[/g, "\n\n~[");

        chunkTranscriptions.push(transcriptionText);

        previousTranscription = getLastNLines(transcriptionText, 20);
      }
    } catch (error) {
      console.error(`Failed to transcribe chunk ${i + 1}:`, error);
      await saveTranscriptionOutput(transcriptionDir, {
        timestamp: Date.now(),
        chunkIndex: i,
        prompt,
        response: "",
        error: error instanceof Error ? error.message : String(error),
      });
      chunkTranscriptions.push(`\n[Transcription error for chunk ${i + 1}]\n`);
    }
  }

  // Combine all content into a single document with proper spacing
  const combinedContent = [
    "# Meeting Description",
    descriptionResult.finalDescription,
    "\n# Audio Analysis",
    descriptionResult.audioDescription,
    "\n# Visual Analysis",
    descriptionResult.imageDescription,
    "\n# Full Transcription",
    ...chunkTranscriptions.map((chunk) => chunk.trim()), // Trim each chunk
  ].join("\n\n");

  // Generate output filenames
  const inputFileName = path.basename(inputFile, path.extname(inputFile));
  const transcriptionPath = path.join(
    outputPath,
    `${inputFileName}_transcription.md`
  );

  // Save the combined content
  fs.writeFileSync(transcriptionPath, combinedContent, "utf-8");

  // Also save raw transcriptions separately
  fs.writeFileSync(
    path.join(transcriptionDir, "raw_transcriptions.json"),
    JSON.stringify(chunkTranscriptions, null, 2)
  );

  if (showProgress) {
    console.log(`Transcription complete. Saved to: ${transcriptionPath}`);
    console.log(`Intermediate outputs saved in: ${transcriptionDir}`);
  }

  return {
    transcriptionPath,
    chunkTranscriptions,
    intermediateOutputPath: transcriptionDir,
  };
}


================================================
File: src/utils/audio-chunk.ts
================================================
import ffmpeg from "fluent-ffmpeg";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

interface ChunkInfo {
  path: string;
  startTime: number;
  endTime: number;
  index: number;
}

interface ProcessingResult {
  chunks: ChunkInfo[];
  tagSample: string;
  workingDirectory: string;
}

interface ProcessOptions {
  chunkMinutes?: number; // Default: 10
  overlapMinutes?: number; // Default: 1
  tagMinutes?: number; // Default: 20
  outputDir?: string; // Default: OS temp directory
}

export async function processAudioFile(
  inputFile: string,
  options: ProcessOptions = {}
): Promise<ProcessingResult> {
  // Set default options
  const {
    chunkMinutes = 10,
    overlapMinutes = 1,
    tagMinutes = 20,
    outputDir = path.join(os.tmpdir(), `audio_processing_${Date.now()}`),
  } = options;

  // Create output directory if it doesn't exist
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Get duration of input file
  const duration = await getFileDuration(inputFile);
  const baseFileName = path.basename(inputFile, path.extname(inputFile));

  // Create promises for all operations
  const processingPromises: Promise<any>[] = [];
  const chunks: ChunkInfo[] = [];

  // Generate tag sample promise
  const tagSamplePath = path.join(outputDir, `${baseFileName}_tag_sample.mp3`);
  if (!fs.existsSync(tagSamplePath)) {
    processingPromises.push(
      createMp3Chunk(inputFile, tagSamplePath, 0, tagMinutes * 60)
    );
  }

  // Calculate chunk boundaries
  const chunkDuration = chunkMinutes * 60;
  const overlapDuration = overlapMinutes * 60;
  const totalChunks = Math.ceil(duration / (chunkDuration - overlapDuration));

  // Generate chunk processing promises
  for (let i = 0; i < totalChunks; i++) {
    const startTime = i * (chunkDuration - overlapDuration);
    const endTime = Math.min(startTime + chunkDuration, duration);
    const chunkPath = path.join(outputDir, `${baseFileName}_chunk_${i}.mp3`);

    // Only process if chunk doesn't exist
    if (!fs.existsSync(chunkPath)) {
      processingPromises.push(
        createMp3Chunk(inputFile, chunkPath, startTime, endTime)
      );
    }

    chunks.push({
      path: chunkPath,
      startTime,
      endTime,
      index: i,
    });
  }

  // Wait for all processing to complete
  await Promise.all(processingPromises);

  return {
    chunks,
    tagSample: tagSamplePath,
    workingDirectory: outputDir,
  };
}

function getFileDuration(filePath: string): Promise<number> {
  return new Promise((resolve, reject) => {
    ffmpeg.ffprobe(filePath, (err, metadata) => {
      if (err) reject(err);
      resolve(metadata.format.duration || 0);
    });
  });
}

function createMp3Chunk(
  inputPath: string,
  outputPath: string,
  startTime: number,
  endTime: number
): Promise<void> {
  return new Promise((resolve, reject) => {
    ffmpeg(inputPath)
      .toFormat("mp3")
      .setStartTime(startTime)
      .setDuration(endTime - startTime)
      .outputOptions([
        "-acodec",
        "libmp3lame",
        "-ar",
        "44100",
        "-ab",
        "192k",
        "-vn", // Disable video
      ])
      .on("end", () => resolve())
      .on("error", (err) => reject(err))
      .save(outputPath);
  });
}

// Example usage:
// console.log("Chunking ", __dirname + "/../../tests/data/speech.mp3", "\n\n");
// const result = await processAudioFile(
//   __dirname + "/../../tests/data/speech.mp3",
//   {
//     chunkMinutes: 1, // Optional: Change chunk size
//     overlapMinutes: 0.5, // Optional: Change overlap duration
//     tagMinutes: 2, // Optional: Change tag sample duration
//     outputDir: __dirname + "/../../tests/chunk_tests", // Optional: Specify output directory
//   }
// );

// console.log("Processed chunks:", result.chunks);
// console.log("Tag sample:", result.tagSample);
// console.log("Working directory:", result.workingDirectory);


================================================
File: src/utils/check-type.ts
================================================
import path from "path";

// First, add the file type checking functions
export function isVideoFile(filePath: string): boolean {
  const videoExtensions = new Set([
    ".flv",
    ".mov",
    ".mpeg",
    ".mpegps",
    ".mpg",
    ".mp4",
    ".webm",
    ".wmv",
    ".3gpp",
  ]);
  return videoExtensions.has(path.extname(filePath).toLowerCase());
}

export function isAudioFile(filePath: string): boolean {
  const audioExtensions = new Set([
    ".aac",
    ".flac",
    ".mp3",
    ".m4a",
    ".mpa",
    ".mpga",
    ".opus",
    ".pcm",
    ".wav",
  ]);
  return audioExtensions.has(path.extname(filePath).toLowerCase());
}


================================================
File: src/utils/ffmpeg-check.ts
================================================
// src/utils/ffmpeg-check.ts
import ffmpeg from "fluent-ffmpeg";
import chalk from "chalk";

export async function checkFFmpeg(): Promise<boolean> {
  return new Promise<boolean>((resolve) => {
    ffmpeg.getAvailableCodecs((err) => {
      if (err) {
        const message = [
          chalk.red.bold("\n❌ FFmpeg is not installed or not properly configured!"),
          chalk.yellow("\nTo use offmute, you need to install FFmpeg:"),
          "\nInstallation instructions:",
          chalk.cyan("\nOn macOS (using Homebrew):"),
          "  brew install ffmpeg",
          chalk.cyan("\nOn Ubuntu/Debian:"),
          "  sudo apt update && sudo apt install ffmpeg",
          chalk.cyan("\nOn Windows:"),
          "  1. Download from: https://www.ffmpeg.org/download.html",
          "  2. Add ffmpeg to your system PATH",
          chalk.cyan("\nUsing Scoop on Windows:"),
          "  scoop install ffmpeg",
          chalk.cyan("\nUsing Chocolatey on Windows:"),
          "  choco install ffmpeg",
          "\nError details:",
          chalk.red(err.message || String(err)),
          "\n",
        ].join("\n");

        console.error(message);
        resolve(false);
        return;
      }
      resolve(true);
    });
  });
}

================================================
File: src/utils/gemini.ts
================================================
import {
  GoogleGenerativeAI,
  GoogleGenerativeAIError,
  Part,
} from "@google/generative-ai";
import { GoogleAIFileManager, FileState } from "@google/generative-ai/server";
import path from "path";

interface FileInput {
  path: string;
  mimeType?: string;
}

interface GeminiResponse {
  text: string;
  files?: Array<{
    name: string;
    uri: string;
    mimeType: string;
  }>;
  error?: string;
}

interface GenerateOptions {
  maxRetries?: number;
  retryDelayMs?: number;
  temperature?: number;
  schema?: any;
}

const MIME_TYPES = new Map([
  // Video formats
  [".flv", "video/x-flv"],
  [".mov", "video/quicktime"],
  [".mpeg", "video/mpeg"],
  [".mpegps", "video/mpegps"],
  [".mpg", "video/mpg"],
  [".mp4", "video/mp4"],
  [".webm", "video/webm"],
  [".wmv", "video/wmv"],
  [".3gpp", "video/3gpp"],
  // Image formats
  [".png", "image/png"],
  [".jpg", "image/jpeg"],
  [".jpeg", "image/jpeg"],
  [".webp", "image/webp"],
  // Audio formats
  [".aac", "audio/aac"],
  [".flac", "audio/flac"],
  [".mp3", "audio/mp3"],
  [".m4a", "audio/m4a"],
  [".mpa", "audio/mpeg"],
  [".mpga", "audio/mpga"],
  [".opus", "audio/opus"],
  [".pcm", "audio/pcm"],
  [".wav", "audio/wav"],
]);

/**
 * Detects MIME type from file extension
 */
function detectMimeType(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();
  const mimeType = MIME_TYPES.get(ext);
  if (!mimeType) {
    throw new Error(`Unsupported file type: ${ext}`);
  }
  return mimeType;
}

/**
 * Handles cleanup of uploaded files
 */
async function cleanupFiles(
  fileManager: GoogleAIFileManager,
  uploadedFiles: Array<{ name: string }>
): Promise<void> {
  await Promise.allSettled(
    uploadedFiles.map(async (file) => {
      try {
        await fileManager.deleteFile(file.name);
        // console.log(`Deleted file: ${file.name}`);
      } catch (error) {
        console.warn(`Failed to delete file ${file.name}:`, error);
      }
    })
  );
}

/**
 * Processes a single attempt at content generation
 */
async function processGenerationAttempt(
  model: GoogleGenerativeAI,
  fileManager: GoogleAIFileManager,
  modelName: string,
  prompt: string,
  files: FileInput[],
  temperature: number = 0,
  schema?: any
): Promise<GeminiResponse> {
  const uploadedFiles: Array<{ name: string }> = [];

  try {
    const modelConfig: any = {
      model: modelName,
      generationConfig: {
        maxOutputTokens: 8192,
        temperature,
      },
    };

    if (schema) {
      modelConfig.generationConfig.responseSchema = schema;
      modelConfig.generationConfig.responseMimeType = "application/json";
    }

    const genModel = model.getGenerativeModel(modelConfig);

    // Upload and process all files
    const processedFiles = await Promise.all(
      files.map(async (file) => {
        const mimeType = file.mimeType || detectMimeType(file.path);

        // Upload file
        const uploadResult = await fileManager.uploadFile(file.path, {
          displayName: path.basename(file.path),
          mimeType,
        });

        uploadedFiles.push({ name: uploadResult.file.name });

        // Wait for processing
        let currentFile = await fileManager.getFile(uploadResult.file.name);
        while (currentFile.state === FileState.PROCESSING) {
          await new Promise((resolve) => setTimeout(resolve, 2000));
          currentFile = await fileManager.getFile(uploadResult.file.name);
        }

        if (currentFile.state === FileState.FAILED) {
          throw new Error(`File processing failed: ${file.path}`);
        }

        return {
          fileData: {
            mimeType: uploadResult.file.mimeType,
            fileUri: uploadResult.file.uri,
          },
          originalFile: uploadResult.file,
        };
      })
    );

    const modelInput: Array<string | Part> = [
      ...processedFiles.map((file) => ({
        fileData: file.fileData,
      })),
      {
        text: prompt,
      },
    ];

    // Generate content
    const result = await genModel.generateContent(modelInput);

    return {
      text: result.response.text(),
      files: processedFiles.map((file) => ({
        name: file.originalFile.name,
        uri: file.originalFile.uri,
        mimeType: file.originalFile.mimeType,
      })),
    };
  } finally {
    // Always cleanup files before returning or throwing
    await cleanupFiles(fileManager, uploadedFiles);
  }
}

/**
 * Main function to process files and generate content using Google's Gemini model
 */
export async function generateWithGemini(
  modelName: string,
  prompt: string,
  files: FileInput[],
  options: GenerateOptions = {}
): Promise<GeminiResponse> {
  const { maxRetries = 1, retryDelayMs = 2000, temperature = 0 } = options;

  const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");
  const fileManager = new GoogleAIFileManager(process.env.GEMINI_API_KEY || "");

  let lastError: Error | undefined;

  // Retry loop for the entire generation process
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await processGenerationAttempt(
        genAI,
        fileManager,
        modelName,
        prompt,
        files,
        temperature,
        options.schema
      );
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt < maxRetries - 1) {
        console.warn(
          `Generation attempt ${attempt + 1}/${maxRetries} failed: ${
            lastError.message
          }`
        );
        await new Promise((resolve) => setTimeout(resolve, retryDelayMs));
      }
    }
  }

  // If we get here, all retries failed
  if (lastError instanceof GoogleGenerativeAIError) {
    return {
      text: "",
      error: `Gemini API Error: ${lastError.message}`,
    };
  }

  return {
    text: "",
    error: `Unexpected error after ${maxRetries} attempts: ${
      lastError?.message || "Unknown error"
    }`,
  };
}

// Example usage:
// console.log("Testing gemini...");
// const response = await generateWithGemini(
//   "gemini-1.5-flash-8b",
//   "Describe what you see and hear in these files",
//   [
//     { path: __dirname + "/../tests/data/speech.mp3" }, // MIME type will be auto-detected
//     // { path: __dirname + "/../tests/data/testimg.png" }, // MIME type will be auto-detected
//   ],
//   process.env.GEMINI_API_KEY || "",
//   {
//     maxRetries: 3,
//     retryDelayMs: 2000,
//     temperature: 0.7,
//   }
// );

// console.log(response.text);
// if (response.error) {
//   console.error(response.error);
// }


================================================
File: src/utils/screenshot.ts
================================================
import ffmpeg from "fluent-ffmpeg";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

interface ScreenshotInfo {
  path: string;
  timestamp: number;
  index: number;
}

interface ScreenshotOptions {
  screenshotCount?: number; // Default: 4
  format?: string; // Default: 'jpg'
  quality?: number; // Default: 100
  outputDir?: string; // Default: OS temp directory
}

export async function extractVideoScreenshots(
  inputFile: string,
  options: ScreenshotOptions = {}
): Promise<ScreenshotInfo[]> {
  // Set default options
  const {
    screenshotCount = 4,
    format = "jpg",
    quality = 100,
    outputDir = path.join(os.tmpdir(), `video_screenshots_${Date.now()}`),
  } = options;

  // Validate input file exists
  if (!fs.existsSync(inputFile)) {
    throw new Error(`Input file not found: ${inputFile}`);
  }

  // Create output directory if it doesn't exist
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Get video duration
  const duration = await getFileDuration(inputFile);
  const baseFileName = path.basename(inputFile, path.extname(inputFile));
  const screenshots: ScreenshotInfo[] = [];
  const processingPromises: Promise<void>[] = [];

  // Calculate timestamps for screenshots (evenly distributed)
  // Start at 1% and end at 99% of duration to avoid black frames
  const startTime = duration * 0.01;
  const endTime = duration * 0.99;
  const interval = (endTime - startTime) / (screenshotCount - 1);

  for (let i = 0; i < screenshotCount; i++) {
    const timestamp = startTime + interval * i;
    const screenshotPath = path.join(
      outputDir,
      `${baseFileName}_screenshot_${i}.${format}`
    );

    // Only process if screenshot doesn't exist
    if (!fs.existsSync(screenshotPath)) {
      processingPromises.push(
        extractScreenshot(inputFile, screenshotPath, timestamp, format, quality)
      );
    }

    screenshots.push({
      path: screenshotPath,
      timestamp,
      index: i,
    });
  }

  // Wait for all screenshots to be processed
  await Promise.all(processingPromises);

  return screenshots;
}

function getFileDuration(filePath: string): Promise<number> {
  return new Promise((resolve, reject) => {
    ffmpeg.ffprobe(filePath, (err, metadata) => {
      if (err) reject(err);
      resolve(metadata.format.duration || 0);
    });
  });
}

function extractScreenshot(
  inputPath: string,
  outputPath: string,
  timestamp: number,
  format: string,
  quality: number
): Promise<void> {
  return new Promise((resolve, reject) => {
    ffmpeg(inputPath)
      .screenshots({
        timestamps: [timestamp],
        filename: path.basename(outputPath),
        folder: path.dirname(outputPath),
        size: "1280x720", // HD resolution
        quality,
      })
      .on("end", () => resolve())
      .on("error", (err) => reject(err));
  });
}

// Example usage:
/*
const screenshots = await extractVideoScreenshots('input.mp4', {
  screenshotCount: 6,         // Optional: Get 6 screenshots instead of default 4
  format: 'png',              // Optional: Use PNG format instead of JPG
  quality: 90,                // Optional: Slightly lower quality (1-100)
  outputDir: './thumbnails'   // Optional: Custom output directory
});

console.log('Generated screenshots:', screenshots);
*/


