import { writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import crypto from 'crypto';

export interface UploadResult {
    success: boolean;
    filename?: string;
    url?: string;
    error?: string;
}

export async function uploadProductImage(file: File): Promise<UploadResult> {
    try {
        // Validate file
        if (!file.type.startsWith('image/')) {
            return { success: false, error: 'File must be an image' };
        }

        if (file.size > 5 * 1024 * 1024) { // 5MB limit
            return { success: false, error: 'File size must be less than 5MB' };
        }

        // Generate unique filename
        const fileExtension = path.extname(file.name);
        const uniqueId = crypto.randomUUID();
        const filename = `${uniqueId}${fileExtension}`;

        // Ensure upload directory exists
        const uploadDir = path.join(process.cwd(), 'static', 'uploads', 'images');
        if (!existsSync(uploadDir)) {
            await mkdir(uploadDir, { recursive: true });
        }

        // Save file
        const buffer = Buffer.from(await file.arrayBuffer());
        const filePath = path.join(uploadDir, filename);
        await writeFile(filePath, buffer);
        console.log(`${new Date().toISOString()} - File uploaded successfully: ${filePath}`);

        return {
            success: true,
            filename: filename,
            url: `/uploads/images/${filename}`
        };
    } catch (error) {
        console.error('File upload error:', error);
        return { success: false, error: 'Upload failed' };
    }
}
