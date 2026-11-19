import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { Type } from "typebox";
import { execFile } from "node:child_process";
import fs from "node:fs/promises";
import { promisify } from "node:util";
import path from "node:path";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, "../..");
const PYTHON_BIN = path.join(PROJECT_ROOT, ".venv", "bin", "python");
const HELPER_SCRIPT = path.join(PROJECT_ROOT, "scripts", "pdf_helper.py");

async function runPdfHelper(args: string[]): Promise<string> {
  try {
    const { stdout } = await execFileAsync(PYTHON_BIN, [HELPER_SCRIPT, ...args], {
      cwd: PROJECT_ROOT,
      maxBuffer: 10 * 1024 * 1024,
    });
    return stdout.trim();
  } catch (err: any) {
    const stderr = err?.stderr?.toString()?.trim();
    const message = stderr || err?.message || "Failed to run pdf_helper.py";
    throw new Error(message);
  }
}

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "pdf_list",
    label: "PDF List",
    description:
      "List all PDF files in the project's pdfs/ folder (or an optional subdirectory). Call this first when the user asks about an uploaded/dropped PDF without giving its exact filename.",
    parameters: Type.Object({
      folder: Type.Optional(
        Type.String({ description: "Subfolder to scan (defaults to 'pdfs')" })
      ),
    }),
    async execute(_toolCallId, params) {
      const targetDir = path.resolve(PROJECT_ROOT, params.folder || "pdfs");
      try {
        const entries = await fs.readdir(targetDir, { withFileTypes: true });
        const pdfs = await Promise.all(
          entries
            .filter((e) => e.isFile() && e.name.toLowerCase().endsWith(".pdf"))
            .map(async (e) => {
              const full = path.join(targetDir, e.name);
              const stat = await fs.stat(full);
              return {
                name: e.name,
                path: path.relative(PROJECT_ROOT, full),
                sizeBytes: stat.size,
              };
            })
        );
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify({ folder: path.relative(PROJECT_ROOT, targetDir), count: pdfs.length, files: pdfs }, null, 2),
            },
          ],
          details: {},
        };
      } catch (err: any) {
        throw new Error(`Failed to list PDFs in ${targetDir}: ${err?.message || err}`);
      }
    },
  });

  pi.registerTool({
    name: "pdf_outline",
    label: "PDF Outline",
    description:
      "Get total page count, metadata, and table of contents (bookmarks) with page numbers for a PDF file. Always call this first when analyzing a new PDF.",
    parameters: Type.Object({
      pdfPath: Type.String({ description: "Path to the PDF file (absolute or relative to workspace)" }),
    }),
    async execute(_toolCallId, params) {
      const output = await runPdfHelper(["outline", params.pdfPath]);
      return {
        content: [{ type: "text", text: output }],
        details: {},
      };
    },
  });

  pi.registerTool({
    name: "pdf_search",
    label: "PDF Search",
    description:
      "Search for a keyword or phrase across all pages of a PDF file. Returns matching page numbers and short text snippets.",
    parameters: Type.Object({
      pdfPath: Type.String({ description: "Path to the PDF file" }),
      query: Type.String({ description: "Keyword or phrase to search for (case-insensitive)" }),
      maxHits: Type.Optional(
        Type.Integer({ description: "Maximum number of matching pages to return (default 15)" })
      ),
    }),
    async execute(_toolCallId, params) {
      const args = ["search", params.pdfPath, params.query];
      if (params.maxHits !== undefined) {
        args.push("--max-hits", String(params.maxHits));
      }
      const output = await runPdfHelper(args);
      return {
        content: [{ type: "text", text: output }],
        details: {},
      };
    },
  });

  pi.registerTool({
    name: "pdf_read_pages",
    label: "PDF Read Pages",
    description:
      "Read a specific range of pages (1-indexed, max 5 pages per call) from a PDF file as clean Markdown with tables preserved.",
    parameters: Type.Object({
      pdfPath: Type.String({ description: "Path to the PDF file" }),
      startPage: Type.Integer({ description: "1-indexed start page number" }),
      endPage: Type.Optional(
        Type.Integer({ description: "1-indexed end page number (defaults to startPage, max 5 pages per call)" })
      ),
    }),
    async execute(_toolCallId, params) {
      const args = ["read", params.pdfPath, String(params.startPage)];
      if (params.endPage !== undefined) {
        args.push(String(params.endPage));
      }
      const output = await runPdfHelper(args);
      return {
        content: [{ type: "text", text: output }],
        details: {},
      };
    },
  });
}
