import { defineConfig } from 'vite'
import laravel from 'laravel-vite-plugin'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [
        laravel({
            input: [
                'resources/css/app.css',
                'resources/js/app.js',   // adjust to your actual entry points
            ],
            refresh: true,
        }),
        react(),
    ],
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8002',
                changeOrigin: true,
                secure: false,
            },
        },
    },
})