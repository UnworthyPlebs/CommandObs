<script>
    import { getcurrentScene, switchScene } from "../obsApi";
    import {onMount} from 'svelte'

    let { sceneData, isActive, onClick, current_path} = $props()

    function scene_click(scenename){
        console.log('Button clicked for scene:', scenename)
        if (!isActive){
            onClick(scenename)
        }
    }

    function instance_click(instance){
        console.log('Button clicked for instance:', instance)
    }
</script>

{#if current_path=== '/api/obs/scenes'}
    <button onclick={() => scene_click(sceneData)}>
        {sceneData}
    </button>
{/if}


