import { UserStatus } from "./user-status.enum";
import { User } from "../user.schema";

interface UserResponseArgs {
	id: string;
	firstName: string;
	lastName: string;
	email: string;
	password: boolean;
	role: string;
	profilePictureUrl: string;
	permissions: string[];
	status: UserStatus;
	showOnPage: boolean;
	createdAt: Date;
	updatedAt: Date;
}

export class UserResponse {
	public id!: string;
	public firstName!: string;
	public lastName!: string;
	public email!: string;
	public password!: boolean;
	public role!: string;
	public profilePictureUrl!: string;
	public permissions!: string[]
	public status!: UserStatus;
	public showOnPage!: boolean;
	public createdAt!: Date;
	public updatedAt!: Date;

	private constructor({
		id,
		firstName,
		lastName,
		email,
		password,
		showOnPage,
		role,
		profilePictureUrl,
		permissions,
		status,
		createdAt,
		updatedAt,
	}: UserResponseArgs) {
		this.id = id;
		this.firstName = firstName;
		this.lastName = lastName;
		this.email = email;
		this.password = password;
		this.role = role;
		this.profilePictureUrl = profilePictureUrl;
		this.permissions = permissions;
		this.showOnPage = showOnPage;
		this.status = status;
		this.createdAt = createdAt;
		this.updatedAt = updatedAt;
	}

	public static fromUser(user: User): UserResponse {
		return new UserResponse({
			id: user._id.toString(),
			firstName: user.firstName,
			lastName: user.lastName,
			email: user.email,
			password: !!user.password,
			role: user.role,
			profilePictureUrl: user.profilePictureUrl,
			permissions: user.permissions,
			showOnPage: user.showOnPage,
			status: user.status,
			createdAt: user.createdAt,
			updatedAt: user.updatedAt
		});
	}
}

