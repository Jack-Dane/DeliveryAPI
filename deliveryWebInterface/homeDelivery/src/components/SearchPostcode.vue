
<script>

export default {

    data: () => ({
        postcode: null,
    }),

    methods: {
        changePostcode () {
            this.$router.push({name: "home", query: {"postcode": this.postcode}});
        }
    }

}

</script>

<template>
    <input type="text" v-model="postcode"/>
    <button v-on:click="changePostcode">Search Postcode</button>
</template>
