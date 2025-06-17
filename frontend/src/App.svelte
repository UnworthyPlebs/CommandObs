<script>
  import './lib/SceneButton.svelte'
  import SceneHandler from './lib/SceneHandler.svelte';
  import { navigateSignup, navigateLogin, addInstance, navigateQuick, get_instances, sessionData } from './obsApi'
  import { onMount } from 'svelte'

  let current_path = $state('')
  let instances = $state(null)
  let connections = $state([])
  let data = sessionData()
  let scene_list = data.scenes
  onMount(async() =>{
    current_path = window.location.pathname
    try{
      instances = await get_instances()
      connections = instances.connections || []
      console.log('Instances loaded:', instances)
      console.log('Connections:', connections)
    }catch (error){
      console.error('Failed to load instances:', error)
    }
  })

  console.log(current_path)
  console.log('tests')
</script>
<main>
  <h1>Command Obs </h1>
</main>

{#if current_path === '/'}
<button onclick={()=>navigateLogin()}> Login </button>
<button onclick={()=>navigateSignup()}> Signup </button>
<button onclick = {()=>navigateQuick()}> Quick Connect </button>
{/if}


{#if current_path === '/api/instances'}
  {#each connections as connection}
    <button onclick={()=> gotoInstance()}>{connection.name}</button>
  {/each}
  <button onclick={()=>addInstance()}> Add instance</button>
{/if}

{#if current_path === '/quickConnect'}
  <button onclick={()=>addInstance()}> Add instance</button>
{/if}

{#if current_path === '/quickScenes'}
  <SceneHandler />
{/if}


<style>
  .logo {
    height: 6em;
    padding: 1.5em;
    will-change: filter;
    transition: filter 300ms;
  }
  .logo:hover {
    filter: drop-shadow(0 0 2em #646cffaa);
  }
  .logo.svelte:hover {
    filter: drop-shadow(0 0 2em #ff3e00aa);
  }
  .read-the-docs {
    color: #888;
  }
</style>
