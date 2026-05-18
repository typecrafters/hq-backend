import { IsArray, IsBoolean, IsEmail, IsNotEmpty, IsString } from "class-validator";

export class CreateUserRequest {
    @IsString()
    @IsNotEmpty()
    firstName!: string;

    @IsString()
    @IsNotEmpty()
    lastName!: string;

    @IsEmail()
    @IsNotEmpty()
    email!: string;

    @IsString()
    @IsNotEmpty()
    role!: string;

    @IsArray()
    @IsString({ each: true })
    permissions!: string[];

    @IsBoolean()
    showOnPage!: boolean;
}