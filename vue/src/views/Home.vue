<template>
	<v-row dense>
		<v-col cols="12">
			<v-card
				class="mx-auto"
				outlined
			>
				<div class="d-flex flex-no-wrap justify-space-between">
					<div>
						<v-card-title class="headline">
							{{ $t( 'welcomemessage' ) }}
						</v-card-title>
						<v-card-subtitle>
							{{ $t( 'tagline' ) }}
						</v-card-subtitle>
						<v-card-text>
							More text would go here and tell people something
							awesome about Toolhub or how to get started using it.
						</v-card-text>
					</div>
					<v-avatar
						class="ma-3"
						size="125"
						tile
					>
						<v-img src="/static/img/logo-community.svg" />
					</v-avatar>
				</div>
			</v-card>
		</v-col>
	</v-row>
</template>
