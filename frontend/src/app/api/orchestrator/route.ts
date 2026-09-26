import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function POST(req: NextRequest) {
  try {
    const { prompt } = await req.json();
    
    // Project root
    const rootDir = path.join(process.cwd(), '..');
    
    // Using double quotes and escaping inner quotes for safety
    const safePrompt = prompt.replace(/"/g, '\\"');
    const command = `python -m mcp.client.orchestrator "${safePrompt}"`;
    
    const { stdout, stderr } = await execAsync(command, { cwd: rootDir });
    
    if (stderr && !stdout) {
      console.error('Python Error:', stderr);
      return NextResponse.json({ error: stderr }, { status: 500 });
    }
    
    // The orchestrator prints "--- Final Response ---" then the response
    const parts = stdout.split('--- Final Response ---');
    const response = parts.length > 1 ? parts[1].trim() : stdout.trim();
    
    return NextResponse.json({ result: response });
  } catch (error: any) {
    console.error('API Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
