import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(req: NextRequest) {
  try {
    const { prompt } = await req.json();
    
    const rootDir = path.join(process.cwd(), '..');
    const safePrompt = prompt.replace(/"/g, '\\"');
    const command = `python -m rag.pipeline "${safePrompt}"`;
    
    const { stdout, stderr } = await execAsync(command, { cwd: rootDir });
    
    if (stderr && !stdout) {
      return NextResponse.json({ error: stderr }, { status: 500 });
    }
    
    // Remove the verbose logging lines if present
    const parts = stdout.split('\n\n');
    let response = stdout.trim();
    if (stdout.includes("Generating interview prep for:")) {
       response = parts.slice(1).join('\n\n').trim();
    }
    
    return NextResponse.json({ result: response });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
