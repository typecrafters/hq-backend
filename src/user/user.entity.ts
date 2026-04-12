import { ObjectId } from "mongodb";
import { Column, CreateDateColumn, Entity, Index, ObjectIdColumn, UpdateDateColumn } from "typeorm";
import type { ColorScheme } from "./dto/color-scheme.enum";

@Entity("users")
export class User {
    @ObjectIdColumn()
    public id!: ObjectId;

    @Column()
    public firstName!: string;

    @Column()
    public lastName!: string;

    @Index({ unique: true })
    @Column()
    public email!: string;

    @Column()
    public password!: string;

    @Column()
    public profilePictureUrl!: string;

    @Column()
    public status!: string;

    @Column()
    public preferredTheme!: ColorScheme;

    @Column()
    public permissions!: string[];

    @CreateDateColumn()
    public createdAt!: Date;

    @UpdateDateColumn()
    public updatedAt!: Date;
}