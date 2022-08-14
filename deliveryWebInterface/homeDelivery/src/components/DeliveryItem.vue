<script>

export default {
    
    data: () => ({
        postcode: null,
        requestURL: "http://localhost:8000",
        requestEndpoint: "/delivery/food/",
        canDeliver: null,
        result: "",
    }),

    props: {
        deliveryItem: String,
        imageURI: String
    },

    methods: {

        async getResponse () {
            let self = this;
            await fetch(
                self.requestURL + self.requestEndpoint + self.deliveryItem + "?postcode=" + this.postcode,
                {
                    headers: {
                        "Content-Type": "application/json",
                    }
                }
            ).then(function(response) {
                return response.json();
            }).then(function(result) {
                self.result = result;
            }).catch(function(error) {
                console.log("Something went wrong: " + error);
            });
        }

    }, 

    watch: {

        $route (newRoute, oldRoute) {
            this.postcode = newRoute.query.postcode;
            this.getResponse();
        }

    }

}

</script>

<template>
  <div>
    <img :src="`/src/assets/DeliveryLogo/${this.imageURI}`" width="50" height="50" v-on:click="getResponse"/>
    <h1>{{ deliveryItem }}</h1>
    <p>{{ result }}</p>
  </div>
</template>

<style scoped>
</style>
