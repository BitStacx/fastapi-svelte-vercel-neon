<script>
    import { onMount } from 'svelte';
    
    let { heading } = $props();
    let pages = $state([]);
    let isLoading = $state(false);
    let error = $state(null);
    
    async function initData() {
        isLoading = true;
        error = null;
        try {
            const response = await fetch('/init-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Init result:', result);
            
            // Refresh pages after init
            await loadPages();
        } catch (err) {
            error = err.message;
            console.error('Failed to initialize data:', err);
        } finally {
            isLoading = false;
        }
    }
    
    async function loadPages() {
        try {
            const response = await fetch('/api/pages');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            pages = await response.json();
        } catch (err) {
            error = err.message;
            console.error('Failed to load pages:', err);
        }
    }
    
    onMount(() => {
        loadPages();
    });
</script>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-4xl font-bold text-center text-gray-800 mb-8">{heading}</h1>
        
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">🚀 FastAPI + Svelte + Vercel + Neon</h2>
            <p class="text-gray-600 mb-6">
                This is a modern full-stack application demonstrating the integration of:
            </p>
            <ul class="list-disc list-inside text-gray-600 mb-6 space-y-2">
                <li><strong>FastAPI</strong> - High-performance Python web framework</li>
                <li><strong>Svelte</strong> - Lightweight frontend framework</li>
                <li><strong>Vercel</strong> - Serverless deployment platform</li>
                <li><strong>Neon</strong> - Cloud PostgreSQL database</li>
            </ul>
            
            <button 
                onclick={initData}
                disabled={isLoading}
                class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
            >
                {isLoading ? '⏳ Initializing...' : '🔄 Initialize Sample Data'}
            </button>
            
            {#if error}
                <div class="mt-4 p-4 bg-red-100 border border-red-300 rounded-lg text-red-700">
                    <strong>Error:</strong> {error}
                </div>
            {/if}
        </div>
        
        {#if pages.length > 0}
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h3 class="text-xl font-semibold text-gray-700 mb-4">📄 Pages in Database</h3>
                <div class="grid gap-4">
                    {#each pages as page}
                        <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h4 class="font-medium text-gray-800">{page.title}</h4>
                                    <p class="text-sm text-gray-500">Name: {page.name} | ID: {page.id}</p>
                                </div>
                                <span class="text-green-600 font-semibold">✓ Active</span>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        {:else if !isLoading}
            <div class="bg-white rounded-lg shadow-lg p-6 text-center">
                <div class="text-gray-400 text-6xl mb-4">📭</div>
                <h3 class="text-xl font-semibold text-gray-700 mb-2">No Pages Found</h3>
                <p class="text-gray-600">Click "Initialize Sample Data" to create some example pages.</p>
            </div>
        {/if}
    </div>
</div>
