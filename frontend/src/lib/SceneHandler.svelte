<script lang="ts">
    import { onMount } from "svelte";
    import { getcurrentScene, switchScene, sessionData } from "../obsApi";
    import { fetchScenes } from "../obsApi";
    import SceneButton from "./SceneButton.svelte";

  let current_scene = $state()
  let loading = $state(true)
  let error_message = $state()
  let scenes = $state()
  let current_path = $state('')
  let token = $state('')

  onMount(()=>{
    current_path = window.location.pathname
    const urlParams = new URLSearchParams(window.location.search)
    token = urlParams.get('token') || ''
    start_loading()
  })

  async function start_loading() {
    loading = true
    error_message = ''
    if (!token){
      error_message = 'No connection token found'
      loading = false
      return
    }

    try{
      const[sceneData, currentSceneData] = await Promise.all([
        fetchScenes(token), 
        getcurrentScene(token)
      ])

      scenes = sceneData
      current_scene = currentSceneData
      console.log(current_scene)
    } catch (error) {
      error_message = error.message
      console.error(error)
    } finally {
      loading = false
    }
   }

  onMount(()=>{
    start_loading()
  })

  async function handle_scene_switch(sceneName) {
    console.log('Switching Scenes')
    current_scene = sceneName
    try{
      await switchScene(sceneName, token)
      console.log('Scene switch successful')
    }catch (error){
      console.error('Error switching scenes:', error_message)
      error_message = `Failed to switch to ${sceneName}: ${error.message}`
    }
  }
</script>


{#if loading}
  <h1>Loading Scenes</h1>
{/if}

<div class = "scene-list">
  {#each scenes as scene}
    <SceneButton 
      sceneData ={scene.sceneName}
      isActive = {current_scene === scene.sceneName}
      onClick = {handle_scene_switch}
      current_path = {current_path}
      />
  {/each}

</div>

<style>
  .scene-list{
    height: 300px;
    overflow-y: scroll;
    scrollbar-width: none;
  }
  .scene-list::-webkit-scrollbar{
    display:none
  }
</style>