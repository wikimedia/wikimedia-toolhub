<template>
	<v-btn
		v-if="$store.state.user.is_authenticated"
		class="ml-2 text-none"
		href="/user/logout/"
		color="secondary"
	>
		{{ $store.state.user.username }}
		<v-icon>mdi-logout</v-icon>
	</v-btn>
	<v-btn
		v-else
		class="ml-2"
		href="/user/login/"
		color="secondary"
	>
		<v-icon>mdi-login</v-icon>
		Login
	</v-btn>
</template>

<script>
export default {
	name: 'UserStatus'
};
</script>
